"""
    Augment GENRE's official EL benchmarks with LLM context
"""

import argparse
import json
import re
import sys
import string
from tqdm import tqdm

sys.path.append("../exceptions")
from exceptions import UnsupportedLLMError, UnsupportedJoinStrategyError

benchmarks = {"ace2004", "msnbc", "aquaint", "clueweb", "wikipedia", "aida_test"}
llms = {"llama-3-70b"}


def augment_datasets(llm_name, join_strategy, original_benchmarks_path, llm_contexts_path, output_path):
    if llm_name.strip() not in llms:
        raise UnsupportedLLMError(llms)
    
    if join_strategy < 0 or join_strategy > 4:
        raise UnsupportedJoinStrategyError()
    
    print(f"[GENRE x {llm_name} x Join-strategy {join_strategy}] benchmarks augmentation progress: ")  
    progress_bar = tqdm(total=len(benchmarks))
    
    for benchmark_name in benchmarks:
        original_benchmark = open(original_benchmarks_path + "/" + benchmark_name + ".jsonl", "r")
        llm_raw_context = open(llm_contexts_path + "/" + llm_name + "/genre/" + benchmark_name + "_" + llm_name + ".jsonl", "r")
        output_file = open(output_path + "/genre/" + llm_name + "/" + benchmark_name + "_join-strat-" + str(join_strategy) + ".jsonl", "w")
        
        case_id = 0
        for line_o, line_llm in zip(original_benchmark, llm_raw_context):
            original_data = json.loads(line_o)
            llm_data = json.loads(line_llm)

            mention = original_data["meta"]["mention"]
            original_context_left = original_data["meta"]["left_context"]
            original_context_right = original_data["meta"]["right_context"]
            original_full_context = (original_context_left + " {} ".format(mention) + original_context_right).strip() 

            llm_context = llm_data["llm_context"]

            # Align LLM context's format to GENRE's format
            i = 0
            while i < len(llm_context):
                if llm_context[i] in string.punctuation:
                    llm_context = llm_context[:i] + llm_context[i+1:]
                else: 
                    i += 1
            llm_context = (' '.join(llm_context.split())).strip() 

            # Find mention offset for LLM-generated context
            llm_offset = 0
            llm_data_lower = llm_context.lower()
            mention_lower = mention.lower()
            llm_mention_length = len(mention_lower) 

            if mention_lower == '*':  # re module encounters error when reading '*', change to readable form
                mention_lower = '[*]'
            temp_offset = (re.search(mention_lower, llm_data_lower))  

            if temp_offset is None:  # Search mention again with punctuation removed
                mention_lower_no_punc = re.sub(r'[^\w\s]','',mention_lower)
                temp_offset = (re.search(mention_lower_no_punc, llm_data_lower))
                llm_mention_length = len(mention_lower_no_punc) 
                
            if temp_offset is None:  # If the LLM context does not include the mention, add the mention to the start
                llm_context = mention + " " + llm_context 
                llm_offset = 0
                llm_mention_length = len(mention_lower)
            else:
                llm_offset = temp_offset.span()[0]

            # Augment benchmark with LLM-generated context
            if join_strategy == 0:
                new_context_left = (llm_context[:llm_offset]).strip()
                new_context_right = (llm_context[llm_offset + llm_mention_length:]).strip()
            elif join_strategy == 1:
                new_context_left = (llm_context[:llm_offset]).strip()
                new_context_right = (llm_context[llm_offset + llm_mention_length:]).strip() + " " + original_full_context
            elif join_strategy == 2:
                new_context_left = llm_context + " " + original_context_left
                new_context_right = original_context_right
            elif join_strategy == 3:
                new_context_left = original_full_context + " " + (llm_context[:llm_offset]).strip()
                new_context_right = (llm_context[llm_offset + llm_mention_length:]).strip()
            elif join_strategy == 4:
                new_context_left = original_context_left
                new_context_right = original_context_right + " " + llm_context
            else: 
                raise UnsupportedJoinStrategyError()

            # Normalize context to GENRE's acceptable window size
            start_delimiter = "[START_ENT]"
            end_delimiter = "[END_ENT]"
            max_length = 384 - 18

            input = new_context_left + " {} ".format(start_delimiter) + mention + " {} ".format(end_delimiter) + new_context_right
            input = (' '.join(input.split())).strip() 
            
            # Normalize context to acceptable window size, adapted from GENRE's official source code
            if len(input.split(" ")) <= max_length:
                        new_input = (
                            new_context_left
                            + " {} ".format(start_delimiter)
                            + mention
                            + " {} ".format(end_delimiter)
                            + new_context_right
                        ).strip()
            elif len(new_context_left.split(" ")) <= max_length // 2:
                        new_input = (
                            new_context_left
                            + " {} ".format(start_delimiter)
                            + mention
                            + " {} ".format(end_delimiter)
                            + " ".join(
                                new_context_right.split(" ")[
                                    : max_length - len(new_context_left.split(" "))
                                    ]
                                )
                        ).strip()
                        new_context_right = " ".join(
                                new_context_right.split(" ")[
                                    : max_length - len(new_context_left.split(" "))
                                    ]
                                )
            elif len(new_context_right.split(" ")) <= max_length // 2:
                        new_input = (
                            " ".join(
                                new_context_left.split(" ")[
                                    len(new_context_right.split(" ")) - max_length :
                                ]
                            )
                            + " {} ".format(start_delimiter)
                            + mention
                            + " {} ".format(end_delimiter)
                            + new_context_right
                        ).strip()
                        new_context_left = " ".join(
                                new_context_left.split(" ")[
                                    len(new_context_right.split(" ")) - max_length :
                                ]
                            )
            else:
                        new_input = (
                            " ".join(new_context_left.split(" ")[-max_length // 2 :])
                            + " {} ".format(start_delimiter)
                            + mention
                            + " {} ".format(end_delimiter)
                            + " ".join(new_context_right.split(" ")[: max_length // 2])
                        ).strip()
                        new_context_left = " ".join(new_context_left.split(" ")[-max_length // 2 :])
                        new_context_right = " ".join(new_context_right.split(" ")[: max_length // 2])

            # Synthesize augmented context
            original_data["meta"]["left_context"] = new_context_left
            original_data["meta"]["right_context"] = new_context_right
            original_data["input"] = new_input

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
        default="../datasets/original_el_benchmarks/genre",
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
    