"""Documented model-specific delivery controls; frozen task text stays intact."""


def adapter_receipt(model_id):
    if model_id == 'nemotron-49b':
        return {'version': 'nemotron-no-think-1', 'system_suffix': '\n\n/no_think',
                'purpose': 'Native template consumes /no_think and adds an empty think prefix; preserves frozen system and task text.',
                'source': 'https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5#quick-start-and-usage-recommendations'}
    return None


def messages(model_id,system,prompt):
    adapter=adapter_receipt(model_id)
    return [{'role':'system','content':system+(adapter['system_suffix'] if adapter else '')},
            {'role':'user','content':prompt}]
