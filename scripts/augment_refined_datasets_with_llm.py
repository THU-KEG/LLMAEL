"""
    Augment ReFinED's official EL benchmarks with LLM context
"""

import argparse
import json
import re
import sys
import operator
from tqdm import tqdm

sys.path.append("../exceptions")
from exceptions import UnsupportedLLMError, UnsupportedJoinStrategyError, MentionNotFoundError, InconsistentMentionError

benchmarks = {"ace2004", "msnbc", "aquaint", "clueweb", "wikipedia", "aida_test", "aida_dev", "aida_train"} 
llms = {"llama-3-70b", "gpt-3.5-turbo", "glm-4"}


def augment_datasets(llm_name, join_strategy, original_benchmarks_path, llm_contexts_path, output_path):
    if llm_name.strip() not in llms:
        raise UnsupportedLLMError(llms)
    
    if join_strategy < 0 or join_strategy > 4:
        raise UnsupportedJoinStrategyError()
    
    if llm_name.strip() != "llama-3-70b":
        benchmarks.remove("clueweb")
        benchmarks.remove("aida_test")
        benchmarks.remove("aida_dev")
        benchmarks.remove("aida_train")
        
    print(f"[ReFinED x {llm_name} x Join-strategy {join_strategy}] benchmarks augmentation progress: ")  
    progress_bar = tqdm(total=len(benchmarks))
    
    for benchmark_name in benchmarks:
        if "aida" in benchmark_name:
            is_aida = True
            mentions_list_name = "spans"
            original_benchmark_name = benchmark_name
        else:
            is_aida = False
            mentions_list_name = "mentions"
            original_benchmark_name = benchmark_name + "_parsed"
            
        original_benchmark = open(original_benchmarks_path + "/" + original_benchmark_name + ".json", "r")
        llm_raw_context = open(llm_contexts_path + "/" + llm_name + "/refined/" + benchmark_name + "_" + llm_name + ".jsonl", "r")
        output_file = open(output_path + "/refined/" + llm_name + "/" + benchmark_name + "_join-strat-" + str(join_strategy) + ".jsonl", "w")
        
        case_id = 0  # aida_train case_id 11136: the brackets are not closed. Manually fixed in the original aida_train dataset
        for line_o, line_llm in zip(original_benchmark, llm_raw_context):
            original_data = json.loads(line_o)
            llm_data = json.loads(line_llm)

            original_data["id"]  = llm_data["id"]

            original_context = original_data["text"]
            original_offset = original_data[mentions_list_name][0]["start"] 
            mention_length = original_data[mentions_list_name][0]["length"]
            llm_context = llm_data["llm_context"]

            if is_aida:
                mention = original_data["text"][original_offset:original_offset + mention_length]
            else:
                mention = original_data[mentions_list_name][0]["text"]

            # Find mention offset for LLM-generated context
            llm_offset = 0
            llm_data_lower = llm_context.lower()
            mention_lower = mention.lower()
            llm_mention_length = len(mention_lower) 
            
            if (operator.contains(mention_lower, "*")):
                mention_lower = mention_lower.replace("*", "[*]")  # re module encounters error when reading '*', change to readable form
                
            temp_offset = (re.search(mention_lower, llm_data_lower))  

            if temp_offset is None:  # Search mention again with punctuation removed
                mention_lower_no_punc = re.sub(r'[^\w\s]','',mention_lower)
                temp_offset = (re.search(mention_lower_no_punc, llm_data_lower))
                llm_mention_length = len(mention_lower_no_punc)  
                
            if temp_offset is None:  # If the LLM context does not include the mention, add the mention to the start
                llm_context = mention + ": " + llm_context
                llm_offset = 0
                llm_mention_length = len(mention_lower) 
            else: 
                llm_offset = temp_offset.span()[0]

            # Special case debug
            original_context =  original_context.replace("&amp;", "&")  

            # Update original_offset
            new_original_offset = original_offset
            
            # Find mention for original context
            ## Search mention to the left of current original_offset
            while (new_original_offset >= 0 and original_context[new_original_offset:new_original_offset + len(mention)] != mention):
                new_original_offset -= 1 
            ## Search mention to the right of current original_offset
            if (original_context[new_original_offset:new_original_offset + len(mention)] != mention):
                new_original_offset = original_offset + 1
                while (new_original_offset < len(original_context) and original_context[new_original_offset:new_original_offset + len(mention)] != mention):
                    new_original_offset += 1 
            ## Didn't find mention on both sides
            if (original_context[new_original_offset:new_original_offset + len(mention)] != mention):
                raise MentionNotFoundError(case_id)

            # Augment benchmark with LLM-generated context
            final_llm_context = llm_context[:llm_offset] + mention + llm_context[llm_offset + llm_mention_length:] 
            
            if join_strategy == 0:
                original_data["text"] = final_llm_context
                original_data[mentions_list_name][0]["start"] = llm_offset
            elif join_strategy == 1:
                original_data["text"] = final_llm_context + "\n" + original_context
                original_data[mentions_list_name][0]["start"] = llm_offset
            elif join_strategy == 2:
                original_data["text"] = final_llm_context + "\n" + original_context
                original_data[mentions_list_name][0]["start"] = len(final_llm_context + "\n") + new_original_offset
            elif join_strategy == 3:
                original_data["text"] = original_context + "\n" + final_llm_context
                original_data[mentions_list_name][0]["start"] = len(original_context + "\n") + llm_offset
            elif join_strategy == 4:
                original_data["text"] = original_context + "\n" + final_llm_context
                original_data[mentions_list_name][0]["start"] = new_original_offset
            else: 
                raise UnsupportedJoinStrategyError()

            # Mention check
            final_offset = original_data[mentions_list_name][0]["start"] 
            mention_check = original_data["text"][final_offset:final_offset + mention_length]        
            
            if mention_check != mention:  # There are some mention offset errors in the clueweb, msnbc, and wikipedia datasets, need manual correction
                raise InconsistentMentionError(case_id)
                
            # Record original contexts and offsets
            original_data["original_context"] = original_context
            original_data["original_start"] = original_offset

            json.dump(original_data, output_file)
            output_file.write("\n")

            case_id += 1
            
        progress_bar.update(1)
        
    progress_bar.close()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--llm_name",
        default="llama-3-70b",
        type=str,
        help="LLM used",
    )
    parser.add_argument(
        "--join_strategy",
        default=4,
        type=int,
        help="Context-joining strategy to combine the original and LLM contexts",
    )
    parser.add_argument(
        "--original_benchmarks_path",
        default="../datasets/original_el_benchmarks/refined",
        type=str,
        help="Path of original EL benchmarks",
    )
    parser.add_argument(
        "--llm_contexts_path",
        default="../datasets/llm_raw_augmentations",
        type=str,
        help="Path of raw LLM augmentations",
    )
    parser.add_argument(
        "--output_path",
        default="../datasets/llm_augmented_el_benchmarks",
        type=str,
        help="Output path for LLM augmented benchmarks",
    )
    
    args = parser.parse_args()
    
    augment_datasets(args.llm_name, args.join_strategy, args.original_benchmarks_path, args.llm_contexts_path, args.output_path)
    