
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/07_batchnorm.ipynb

from exp.nb_06 import *

from torch.jit import ScriptModule, script_method, script
from typing import *

class BatchNormJit(ScriptModule):
    def __init__(self, nf, mom=0.1, eps=1e-5):
        super().__init__()
        self.mults = nn.Parameter(torch.ones (1,nf,1,1))
        self.adds  = nn.Parameter(torch.zeros(1,nf,1,1))
        self.register_buffer('vars',  torch.zeros(1,nf,1,1))
        self.register_buffer('means', torch.zeros(1,nf,1,1))
        self.register_buffer('steps', tensor(0))

    @script_method
    def update_stats(self, x):
        self.steps += 1
        mom,eps = 0.1,1e-5
        m, invstd = torch.batch_norm_stats(x, eps)
        views = (1,-1,1,1)
        m = m.view(*views)
        v = (invstd**-2).view(*views)
        if bool(self.steps>0):
            m = self.means*(1-mom) + m*mom
            v = self.vars *(1-mom) + v*mom
        self.means.copy_(m.detach())
        self.vars .copy_(v.detach())

    @script_method
    def forward(self, x):
        if self.training: self.update_stats(x)
        # squeeze.unsqueeze is to create a barrier to trick the fuser
        factor = (self.mults/self.vars.sqrt()).squeeze(-1).unsqueeze(-1)
        offset = (self.adds-self.means).squeeze(-1).unsqueeze(-1)
        return factor * (x+offset)

def conv_layer(ni, nf, ks=3, stride=2, bn=True, **kwargs):
    layers = [nn.Conv2d(ni, nf, ks, padding=ks//2, stride=stride, bias=not bn),
              GeneralRelu(**kwargs)]
    if bn: layers.append(nn.BatchNorm2d(nf, eps=1e-5))
    return nn.Sequential(*layers)