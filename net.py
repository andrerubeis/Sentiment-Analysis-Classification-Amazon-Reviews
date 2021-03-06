'''
To do:
- correct forget gate function
- update embedding with ELMO
'''

import torch
import torch.nn as nn
from torch.nn.parameter import Parameter
import params  # aggiunto params file in cui salviamo tutti gli hyperparameters
from lstm_cell import LSTMCell  # importo la notra LSTMCell
from attention_layer import AttentionLayer
import numpy as np


class SentimentAnalysis(nn.Module):
    def __init__(self, batch_size, hidden_dim, embedding_size, dropout_rate):
        super(SentimentAnalysis, self).__init__()

        self.batch_size = batch_size
        self.hidden_dim = hidden_dim
        self.input_size = embedding_size
        self.num_classes = params.NUM_CLASSES
        # Dropout
        self.dropout = nn.Dropout(dropout_rate)
        # Bi-LSTM
        # Forward and backward
        self.lstm_cell_forward = LSTMCell(self.input_size, self.hidden_dim, self.hidden_dim)  # x,h,c
        self.lstm_cell_backward = LSTMCell(self.input_size, self.hidden_dim, self.hidden_dim)  # x,h,c
        # LSTM layer
        self.lstm_cell = LSTMCell(self.hidden_dim * 2, self.hidden_dim * 2, self.hidden_dim * 2)

        # Linear layer
        self.linear = nn.Linear(self.hidden_dim * 2, self.num_classes)

        # Attention parameters
        self.attention = AttentionLayer(self.hidden_dim)

        self.fc = nn.Linear(self.hidden_dim*2, self.hidden_dim*2)
        self.relu = torch.nn.ReLU()
        self.dropout2 = nn.Dropout(dropout_rate)

    def forward(self, x):
        hs_forward = Parameter(torch.zeros(x.size(0), self.hidden_dim, device=params.DEVICE))
        cs_forward = Parameter(torch.zeros(x.size(0), self.hidden_dim, device=params.DEVICE))
        hs_backward = Parameter(torch.zeros(x.size(0), self.hidden_dim, device=params.DEVICE))
        cs_backward = Parameter(torch.zeros(x.size(0), self.hidden_dim, device=params.DEVICE))

        hs_lstm = Parameter(torch.zeros(x.size(0), self.hidden_dim * 2, device=params.DEVICE))
        cs_lstm = Parameter(torch.zeros(x.size(0), self.hidden_dim * 2, device=params.DEVICE))

        # Weights initialization
        # torch.nn.init.kaiming_normal_(cs_forward)
        # torch.nn.init.kaiming_normal_(hs_backward)
        # torch.nn.init.kaiming_normal_(cs_backward)
        # torch.nn.init.kaiming_normal_(hs_lstm)
        # torch.nn.init.kaiming_normal_(hs_forward)
        # torch.nn.init.kaiming_normal_(cs_lstm)

        forward = []
        backward = []

        # Unfolding Bi-LSTM
        # Forward
        for i in range(x.size(1)):  # [Frase1 Prova, Frase2] -> [ [emb(frase1), emb(prova)], [emb(frase2), embvuoto]
            inp = x[:, i, :]
            hs_forward, cs_forward = self.lstm_cell_forward(inp, (hs_forward, cs_forward))
            forward.append(hs_forward)

        # Backward
        for i in reversed(range(x.size(1))):
            inp = x[:, i, :]
            hs_backward, cs_backward = self.lstm_cell_backward(inp, (hs_backward, cs_backward))
            backward.append(hs_backward)
        backward.reverse()
        # LSTM
        hidden_states_lstm = torch.tensor((), device=params.DEVICE)
        for fwd, bwd in zip(forward, backward):
            input_tensor = torch.cat((fwd, bwd), 1)
            hs_lstm, cs_lstm = self.lstm_cell(input_tensor, (hs_lstm, cs_lstm))
            hidden_states_lstm = torch.cat((hidden_states_lstm, hs_lstm.unsqueeze(2)), dim=-1)

        hs_lstm, attention = self.attention(hidden_states_lstm)
        hs_lstm = self.dropout(hs_lstm)
        hs_lstm = self.fc(hs_lstm)
        hs_lstm = self.relu(hs_lstm)
        hs_lstm = self.dropout2(hs_lstm)
        out = self.linear(hs_lstm)
        return out, attention
