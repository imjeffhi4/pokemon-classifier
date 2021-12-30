import torch
import pytorch_lightning as pl
from PIL import Image
from transformers import ViTForImageClassification, ViTFeatureExtractor
import os
import re
from tqdm import tqdm
from transformers.optimization import AdamW
from pytorch_lightning.callbacks import Callback
from torch.utils.data import random_split
save_path = f"augmented_model"
if not os.path.isdir(save_path):
    os.mkdir(save_path)

import json
with open('pokemon_data.json', 'r', encoding='utf-8') as r:
    pokedex = json.load(r)

class PokemonClassifier(pl.LightningModule):
    def __init__(self): 
        super().__init__()
        model_name = 'google/vit-base-patch16-224' # name of the pretrained model
        self.model = ViTForImageClassification.from_pretrained(model_name)
        self.feature_extractor = ViTFeatureExtractor.from_pretrained(model_name) # resizes and normalizes 
        self.batch_size = 12 # use whatever you can fit in memory
        self.lr = 5e-5
        num_pokemon = 898 # total number of pokemon/labels
        self.model.classifier = torch.nn.Linear(768, num_pokemon) # Output layer should match the total number of pokemon for classification
        self.model.num_labels = num_pokemon
        self.update_config()

    def update_config(self):
        """Updating the config file with Pokemon labels"""
        id2label, label2id = {}, {}
        for pokedex_num, item in pokedex.items():
            num = int(pokedex_num) -1 
            id2label[num] = item['Name']
            label2id[item['Name']] = num
        self.model.config.id2label = id2label
        self.model.config.label2id = label2id

    def get_datasets(self, path):
        """Gets all images in given directory, converts to appropriate tensor format, and returns tuple with image tensor and label"""
        images = os.listdir(path)
        for image_name in tqdm(images): 
            image_tensor =  self.feature_extractor(images=Image.open(f"{path}/{image_name}").convert('RGB'), return_tensors="pt") # Input image
            label_tensor = torch.zeros(1, dtype=torch.long)
            pokedex_num = int(re.findall('^([^_]+)', image_name)[0]) - 1 
            label_tensor[0] = pokedex_num
            yield image_tensor, label_tensor

    def prepare_data(self): 
        train_data = tuple(self.get_datasets('../data_collection/training_data_augmented'))
        self.train_ds = random_split(train_data, [len(train_data), 0])[0]
        test_data = tuple(self.get_datasets('../data_collection/testing_data'))
        self.test_ds = random_split(test_data, [len(test_data), 0])[0]

    def forward(self, batch, batch_idx):
        return self.model(batch[0]['pixel_values'].squeeze(), labels=batch[1].squeeze())

    def training_step(self, batch, batch_idx):
        loss = self(batch, batch_idx)[0]
        self.log('train_loss', loss)
        return loss

    def validation_step(self, batch, batch_idx):
        output = self(batch, batch_idx)
        predicted_labels = output[1].argmax(-1)
        real_labels = batch[1].squeeze()
        accuracy = torch.sum(predicted_labels ==real_labels)/self.batch_size
        self.log('val_accuracy', accuracy)
        loss = output[0]
        self.log('val_loss', loss)
        
    def train_dataloader(self):
        return torch.utils.data.DataLoader(self.train_ds, batch_size=self.batch_size, drop_last=True, shuffle=True, num_workers=0)

    def val_dataloader(self):
        return torch.utils.data.DataLoader(self.test_ds, batch_size=self.batch_size, drop_last=False, shuffle=False, num_workers=0)

    def configure_optimizers(self):
        return AdamW(self.parameters(), lr=self.lr, weight_decay=0.01)

class SaveCallback(Callback):
    def on_epoch_start(self, trainer, pl_module):
        if pl_module.current_epoch > 0:
            current_epoch = str(pl_module.current_epoch)
            fn = f'epoch_{current_epoch}'
            new_path = f"{save_path}/{fn}/"
            if fn not in os.listdir(save_path):
                os.mkdir(new_path)
            pl_module.model.save_pretrained(new_path)


PokeModel = PokemonClassifier()
trainer = pl.Trainer(
    accumulate_grad_batches= 4,
    precision = 'bf16', # only use if you have an Ampere GPU or newer
    default_root_dir='logs',
    gpus= -1,
    max_epochs=5,
    callbacks=[SaveCallback()],
    val_check_interval=0.1,
    logger=pl.loggers.TensorBoardLogger('logs/', name='vit_with_augmentation', version=0)
)
trainer.fit(PokeModel)