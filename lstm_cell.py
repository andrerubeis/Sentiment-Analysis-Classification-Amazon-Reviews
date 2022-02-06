# -*- coding: utf-8 -*-
"""lstm_cell.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JM4DfNHiAYtlQ4T1j3ECIIp0tdYRhWSJ
"""
import torch
import torch.nn as nn
from torch.nn.parameter import Parameter

class LSTMCell(nn.Module):
    def __init__(self, input_size, hidden_size, cell_size): # in teoria hidden_size e cell_size uguali ma per adesso passiamo entrambi
        super(LSTMCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.W = Parameter(torch.randn(4 * hidden_size, input_size)) #w_ih
        self.U = Parameter(torch.randn(4 * hidden_size, hidden_size)) #w_hh
        self.V = Parameter(torch.randn(4 * hidden_size,  cell_size)) #controllare se è giusto hidden size
        self.bias_ih = Parameter(torch.randn(4 * hidden_size))
        self.cell_state = Parameter(torch.zeros(cell_size))
        #self.hidden_state = Parameter(torch.zeros(hidden_size))
        self.W_attention = Parameter(torch.randn(hidden_size, hidden_size))
        self.bias_attention = Parameter(torch.randn(hidden_size))
        self.hidden_states = [Parameter(torch.zeros(hidden_size))] 

    def forward(self, input, state): #state = (hx, cx)
        # type: (Tensor, Tuple[Tensor, Tensor]) -> Tuple[Tensor, Tuple[Tensor, Tensor]]
       
        gates = (torch.mm(input, self.W.t()) + self.bias_ih + torch.mm(self.hidden_states[-1], self.U.t()) +  torch.mm(self.cell_state, self.V.t()))
        ingate, forgetgate, cellgate, outgate = gates.chunk(4, 1)
        
        ingate = torch.sigmoid(ingate)
        forgetgate = torch.sigmoid(forgetgate)
        cellgate = torch.tanh(cellgate)
        outgate = torch.sigmoid(outgate)

        cy = (forgetgate * state[1]) + (ingate * cellgate)
        hy = outgate * torch.tanh(cy)
        
        self.hidden_states.append(hy) #controlla che non dia errore
        self.cell_state = cy
        return hy, cy


    def attention_layer(self):
      u = []
      for i in range(len(self.hidden_states)):
        u_it = torch.tanh(torch.mm(self.W_attention, self.hidden_states[i])+self.bias_attention) # il nostro paper usa tan ma abbiamo messo tanh
        u.append(u_it)
      attention_vector = torch.randn(hidden_size) #u_w global context vector
      a = torch.softmax(torch.mm(u, attention_vector))
      s = torch.mm(a, self.hidden_state)