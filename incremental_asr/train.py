import os
import utils
import torch
import modules
import sentencepiece
from tqdm import tqdm

if __name__ == "__main__":
    configs = utils.parsing.parse_args_and_configs()

    if not configs['skip_data_preparation']:
        utils.data.prepare_annotation_files(configs)

    if not os.path.exists(configs['result_dir']):
        os.makedirs(configs['result_dir'], exist_ok=True)

    tokenizer = sentencepiece.SentencePieceProcessor(
        model_file=configs['tokenizer_path'])

    train_loader = modules.data.SpeechDataLoader('train', configs, tokenizer)
    valid_loader = modules.data.SpeechDataLoader('valid', configs, tokenizer)
    test_loader = modules.data.SpeechDataLoader('test', configs, tokenizer)

    model = modules.model.ASR(configs)
    optimizer = torch.optim.AdamW(model.parameters(), lr=configs['learning_rate'])
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer=optimizer,
        mode='min',
        factor=0.5,
        patience=2
    )
    
    def average(input):
        sum = 0
        for i in input:
            sum += i
        
        return sum / len(input)

    losses = []
    with tqdm(train_loader, desc='Training') as bar:
        for batch in bar:
            loss = model(batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            losses.append(loss.item())
            bar.set_postfix(loss=average(losses))
            

