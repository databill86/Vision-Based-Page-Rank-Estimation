import os
import torch
from sacred.observers import MongoObserver
from rank_predictor.trainer.logging import setup_custom_logger
from rank_predictor.trainer.lr_scheduler.warmup_scheduler import GradualWarmupScheduler
from rank_predictor.trainer.ranking.probabilistic_loss import ProbabilisticLoss
from sacred import Experiment
from rank_predictor.data.v2.pagerank_dataset_screenshots import DatasetV2Screenshots
from rank_predictor.model.graph_extractor_full import ScreenshotsFeatureExtractorWithHead
from rank_predictor.trainer.training_run import FeatureExtractorTrainingRun

name = 'featextr_08_wob'
ex = Experiment(name)

ex.observers.append(MongoObserver.create(url='mongodb://localhost:27017/sacred'))


@ex.config
def run_config():
    learning_rate: float = 1e-5
    batch_size = 2
    epochs = 10
    optimizer = 'adam'
    train_ratio, valid_ratio = .6, .2
    loss = 'ProbabilisticLoss'
    weighting = 'c_ij = c_ij !* w'
    logrank_b = 10
    drop_p = 0.1
    lr_scheduler = 'None'
    lr_scheduler_gamma = 0
    loss_scaling_fac = 1/2


@ex.main
def train(learning_rate: float, batch_size: int, epochs: int, optimizer: str, train_ratio: float, valid_ratio: float,
          loss: str, logrank_b: float, drop_p: float, lr_scheduler: str, lr_scheduler_gamma: float,
          loss_scaling_fac: float) -> str:

    logger = setup_custom_logger('default')

    use_cuda = torch.cuda.is_available()
    device = torch.device('cuda' if use_cuda else 'cpu')
    logger.info("Device: {}".format(device))

    # dataset
    dataset_dir = os.path.expanduser(os.getenv('dataset_v2_path'))
    data = DatasetV2Screenshots.get_threefold(dataset_dir, train_ratio, valid_ratio, logrank_b)

    net = ScreenshotsFeatureExtractorWithHead(drop_p)

    if optimizer == 'adam':
        opt = torch.optim.Adam(net.parameters(), lr=learning_rate)
    else:
        raise ValueError("Unknown optimizer '{}'".format(optimizer))

    if loss == 'ProbabilisticLoss':
        loss = ProbabilisticLoss(loss_scaling_fac)
    else:
        raise ValueError("Unknown loss '{}'".format(loss))

    if lr_scheduler == 'GradualWarmupSchedulerExponentialLR':
        exp_scheduler = torch.optim.lr_scheduler.ExponentialLR(opt, gamma=lr_scheduler_gamma)
        lr_scheduler = GradualWarmupScheduler(opt, multiplier=15, total_epoch=20, after_scheduler=exp_scheduler)
    else:
        lr_scheduler = None

    training_run = FeatureExtractorTrainingRun(ex, name, net, opt, loss, data, batch_size, device, lr_scheduler)
    val_acc = training_run(epochs)

    return "Test acc: {:.4f}".format(val_acc)


if __name__ == '__main__':
    ex.run_commandline()
