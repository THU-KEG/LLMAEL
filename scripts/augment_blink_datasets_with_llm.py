"""
    Augment BLINK's official EL benchmarks with LLM context
"""

import argparse
import json
import re
import sys
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
    
    print(f"[BLINK x {llm_name} x Join-strategy {join_strategy}] benchmarks augmentation progress: ")  
    progress_bar = tqdm(total=len(benchmarks))
    
    for benchmark_name in benchmarks:
        original_benchmark = open(original_benchmarks_path + "/" + benchmark_name + ".jsonl", "r")
        llm_raw_context = open(llm_contexts_path + "/" + llm_name + "/blink/" + benchmark_name + "_" + llm_name + ".jsonl", "r")
        output_file = open(output_path + "/blink/" + llm_name + "/" + benchmark_name + "_join-strat-" + str(join_strategy) + ".jsonl", "w")
        
        case_id = 0
        for line_o, line_llm in zip(original_benchmark, llm_raw_context):
            original_data = json.loads(line_o)
            llm_data = json.loads(line_llm)

            original_context_left = original_data["context_left"]
            original_context_right = original_data["context_right"]

            mention = original_data["mention"]
            llm_context = llm_data["llm_context"]
            
            # Find mention offset for original context
            optional_space = " "
            if (len(original_context_left) == 0): # Only add optional space if context_left is non-empty
                optional_space = ""

            original_offset = len(original_context_left + optional_space)
            original_full_context = original_context_left + optional_space + "{} ".format(mention) + original_context_right

            # Find mention offset for LLM-generated context
            llm_offset = 0
            llm_data_lower = llm_context.lower()
            mention_lower = mention.lower()

            if mention_lower == '*':  # re module encounters error when reading '*', change to readable form
                mention_lower = '[*]'
                
            temp_offset = (re.search(mention_lower, llm_data_lower))  

            if temp_offset is None:  # If the LLM context does not include the mention, add the mention to the start
                llm_context = mention + ": " + llm_context
                llm_offset = 0
            else:
                llm_offset = temp_offset.span()[0]

            # Augment benchmark with LLM-generated context
            if join_strategy == 0:  # LLM context only
                original_data["context_left"] = (llm_context[:llm_offset]).strip()
                original_data["context_right"] = (llm_context[llm_offset + len(mention):]).strip()
            elif join_strategy == 1:  # LLM-Original, LLM offset
                original_data["context_left"] = (llm_context[:llm_offset]).strip()
                original_data["context_right"] = (llm_context[llm_offset + len(mention):]).strip() + "\n" + original_full_context
            elif join_strategy == 2:  # LLM-Original, Original offset
                original_data["context_left"] = llm_context + "\n" + original_context_left
                original_data["context_right"] = original_context_right
            elif join_strategy == 3:  # Original-LLM, LLM offset
                original_data["context_left"] = original_full_context + "\n" + (llm_context[:llm_offset]).strip()
                original_data["context_right"] = (llm_context[llm_offset + len(mention):]).strip()
            elif join_strategy == 4:  # Original-LLM, Original offset
                original_data["context_left"] = original_context_left
                original_data["context_right"] = original_context_right + "\n" + llm_context
            else:
                raise UnsupportedJoinStrategyError()
            
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
        default="../datasets/original_el_benchmarks/blink",
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
    