import re
import torch
import pytorch_lightning as pl
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM



class T5smallFinetuner(pl.LightningModule):
    def __init__(self, model, tokenizer):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.train_losses = []  # Store losses for logging at epoch end
        self.val_losses = []    # Store validation losses for logging at epoch end

    def forward(self, input_ids, attention_mask, decoder_attention_mask=None, labels=None):
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels
        )
        return outputs.loss

    def _step(self, batch):
        source_input_ids, source_attention_mask, target_input_ids, target_attention_mask = batch
        loss = self(
            input_ids=source_input_ids,
            attention_mask=source_attention_mask,
            decoder_attention_mask=target_attention_mask,
            labels=target_input_ids
        )
        return loss

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)
        self.train_losses.append(loss)  # Append the loss for epoch-end logging
        return {"loss": loss}

    def validation_step(self, batch, batch_idx):
        loss = self._step(batch)
        self.val_losses.append(loss)  # Append the validation loss for epoch-end logging
        return {"val_loss": loss}

    def on_train_epoch_end(self):
        # Calculate mean training loss and log it
        avg_train_loss = torch.stack(self.train_losses).mean()
        self.log('train_loss', avg_train_loss, prog_bar=True, logger=True)
        self.train_losses.clear()  # Clear for the next epoch

    def on_validation_epoch_end(self):
        # Calculate mean validation loss and log it
        avg_val_loss = torch.stack(self.val_losses).mean()
        self.log('val_loss', avg_val_loss, prog_bar=True, logger=True)
        self.val_losses.clear()  # Clear for the next epoch

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=2e-5)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=3)
        return {
            'optimizer': optimizer,
            'lr_scheduler': scheduler,
            'monitor': 'val_loss'
        }

