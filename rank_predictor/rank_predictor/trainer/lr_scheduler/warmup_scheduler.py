from typing import Optional

import torch
from torch.optim.lr_scheduler import _LRScheduler


class GradualWarmupScheduler(_LRScheduler):
    """
    Modified version of https://github.com/ildoonet/pytorch-gradual-warmup-lr
    """

    def __init__(self, optimizer: torch.optim.Optimizer, multiplier: float, total_epoch: int,
                 after_scheduler: Optional = None):
        """
        Gradually warm-up(increasing) learning rate in optimizer.
        Proposed in 'Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour'.
        :param optimizer: Wrapped optimizer.
        :param multiplier: Target learning rate = base lr * multiplier.
        :param total_epoch: Target learning rate is reached at total_epoch, gradually.
        :param after_scheduler: After target_epoch, use this scheduler (eg. ReduceLROnPlateau).
        """
        self.multiplier = multiplier
        if self.multiplier <= 1.:
            raise ValueError('multiplier should be greater than 1.')
        self.total_epoch = total_epoch
        self.after_scheduler = after_scheduler
        self.finished = False
        self.last_step = 0
        self.switch_step = 0
        super().__init__(optimizer)

    def get_lr(self):
        if self.last_epoch > self.total_epoch:
            if self.after_scheduler:
                if not self.finished:
                    self.after_scheduler.base_lrs = [base_lr * self.multiplier for base_lr in self.base_lrs]
                    self.finished = True
                return self.after_scheduler.get_lr()
            return [base_lr * self.multiplier for base_lr in self.base_lrs]

        return [base_lr * ((self.multiplier - 1.) * self.last_epoch / self.total_epoch + 1.) for base_lr in self.base_lrs]

    def get_lr(self):
        if self.last_epoch > self.total_epoch:
            if self.after_scheduler:
                if not self.finished:
                    self.after_scheduler.base_lrs = [base_lr * self.multiplier for base_lr in self.base_lrs]
                    self.finished = True
                    self.switch_step = self.last_step
                return self.after_scheduler.get_lr()
            return [base_lr * self.multiplier for base_lr in self.base_lrs]

        return [base_lr * ((self.multiplier - 1.) * self.last_epoch / self.total_epoch + 1.) for base_lr in self.base_lrs]

    def step(self, epoch: Optional[int] = None):
        self.last_step = epoch
        if self.finished and self.after_scheduler:
            return self.after_scheduler.step(epoch - self.switch_step)
        else:
            return super(GradualWarmupScheduler, self).step(epoch)
