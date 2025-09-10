# given a command in the format a string, generate the yaml field args

import argparse

command = """
python train.py \
    --lr 0.0001 --max_epochs 500 \
    --n_dim_hidden 64 --n_dim_latent 32 --batch_size 32 \
    --data_path /volume/mydata/video_analysis \
    --train_set_ratio 0.9 \
    --save_path /volume/code/MMVAE_playground/results/region_motion --session_name th_rl1e_4_zscore_l32 \
    --read_sessions 22R_D1_SFO_MidBrain_g0_imec0_data 22R_D1_SFO_MidBrain_g0_imec1_data \
    --region1 spike_matrix_th.npy --region2 video_motSVD.npy \
    --transform zscore \
    --a_neuron 1 --a_motion 0.1
"""

args = command.split()
print(args)


cmd_list = ["/volume/code/MMVAE_playground/train.py",
          '--lr', '1e-4', '--max_epochs', '1000',
          '--n_dim_hidden', '384', '--n_dim_latent', '96',
          '--batch_size', '32',
          '--data_path', '/volume/mydata/video_analysis',
          '--train_set_ratio', '0.9',
          '--save_path', '/volume/code/MMVAE_playground/results/region_motion',
          '--session_name', 'th_onlyneuron_1000epoch_rl1e-4_n384_l96_bs32_std',
          '--read_sessions','22R_D1_SFO_MidBrain_g0_imec0_data', '22R_D1_SFO_MidBrain_g0_imec1_data',
          '--region1', 'spike_matrix_th.npy', '--region2', 'video_motSVD.npy', '--transform', 'std',
          '--a_neuron', '1', '--a_motion', '1']
cmd = ' '.join(cmd_list)
print(cmd)
