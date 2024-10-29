from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from src.News_Summarizer.summarization import T5smallFinetuner

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("t5-small")
base_model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
prediction_model = T5smallFinetuner(model=base_model, tokenizer=tokenizer)

# Load state dict
state_dict = torch.load('artifacts/t5-small.pt')
prediction_model.load_state_dict(state_dict['model_state_dict'])
prediction_model.eval()
