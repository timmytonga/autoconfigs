# set dataset specific settings to overwrite the generic default args.

default_data_setting_dict = {  # if we would like to set dataset specific params
    'dynamic_default_field': 'dataset',  # this sets the key
    'imagenet': {'n_epochs': 50, 'batch_size': 128, 'log_every': 250,
                 'weight_decay': 1e-4, 'lr': 1e-3, 'model': 'resnet50'},
    'mrpc': {'n_epochs': 3, 'batch_size': 8, 'log_every': 100,
             'weight_decay': 0.0, 'lr': 5e-5, 'optimizer': 'adamw', 'scheduler': 'linear',
             'model': 'bert'},
    'sst2': {'n_epochs': 4, 'batch_size': 16, 'log_every': 100,
             'weight_decay': 0.0, 'lr': 2e-5, 'optimizer': 'adamw', 'scheduler': 'linear',
             'model': 'bert', 'no_test': True},  # Test set doesn't contain labels!!!!
    'mnli': {'n_epochs': 4, 'batch_size': 8, 'log_every': 1000,
             'weight_decay': 0.0, 'lr': 2e-5, 'optimizer': 'adamw', 'scheduler': 'linear',
             'model': 'bert', 'no_test': True},  # Test set doesn't contain labels!!!!
    'imdb': {'n_epochs': 10, 'batch_size': 16, 'log_every': 25,
             'weight_decay': 0.01, 'lr': 2e-5, 'optimizer': 'adamw', 'scheduler': 'linear',
             'model': 'distilbert', 'no_test': False},
    'squad': {'n_epochs': 4, 'batch_size': 64, 'log_every': 25,
              'weight_decay': 0.01, 'lr': 2e-5, 'optimizer': 'adamw', 'scheduler': 'linear',
              'model': 'bert-cased', 'no_test': False},
    'mnist': {'model': 'simple', 'n_epochs': 50, 'batch_size': 128, 'weight_decay': 0,
              'lr': 1e-2, 'log_every': 0},
    'fashion_mnist': {'model': 'wide-resnet-28-10', 'n_epochs': 100, 'batch_size': 256, 'weight_decay': 0,
                      'lr': 1e-2, 'log_every': 100},
    'wikitext': {'model': 'gptbase', 'batch_size': 4, 'optimizer': 'adamw', 'scheduler': 'one_cycle',
                 'weight_decay': 0.1, 'lr': 1e-3, 'dropout': 0.1, 'log_every': 100, 'n_epochs': 1,
                 'sequence_length': 4096, 'turn_on_torch_amp_autocast': True, 'n_accumulate_batches': 4,
                 'pct_start': 0.02}  # see https://openreview.net/pdf?id=UINHuKeWUa top of pg 20 for wikitext default
}

default_scheduler_setting_dict = {
    'dynamic_default_field': 'scheduler',  # this sets the key,
    'one_cycle': {'scheduler_step_every': 'batch'},
    'linear': {'scheduler_step_every': 'batch'},
    'reduce_lr_on_plateau': {'scheduler_step_every': 'epoch'},
}
