# coding = utf-8

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import subprocess

from sys import exit
from scipy.io import wavfile
from scipy.fftpack import fft
from matplotlib.animation import FuncAnimation

#subprocess.call(['ffmpeg', '-i', './input/test.mp3','./output/test.wav'])

sr, music_data = wavfile.read('./output/test.wav')
#F_data = np.abs(fft(music_data)) 
buffer = np.arange(1, 65) #用来做动画的缓冲
fig, ax = plt.subplots(figsize=(18,9)) #画图的对象
ax.axis('off') #关闭坐标轴和边框
sound_chunk_idx = 0 #音频块的索引
chunk_size = 1470 #每次送入stream的chunk

#初始化函数，第一帧
def init():
    ax.set_xlim(1, 65) #横轴的标
    ax.set_ylim(0, 600000) #纵轴的坐标
    return ax.stem(buffer, buffer)

#更新函数，会在动画的每一帧调用
def update(frame):
    xdata = np.arange(1, 65) #共有65个数据点
    ydata = buffer #通过callback函数来改变buffer的值，然后让频谱动起来
    b_c = ax.stem(xdata, ydata, linefmt='--', markerfmt=None) #这里这里stem图
    return b_c #必须有

#音频流回调函数，会在音频chunk播放完后调用
def callback(indata, outdata, frames, time, status):
    frames = chunk_size #每次给流内推入chunk_size个数据
    global sound_chunk_idx

    #下面的if语句用来判断最后的音频不够chunk_size个值，防止程序出错
    if (music_data[chunk_size*sound_chunk_idx:chunk_size*(sound_chunk_idx+1), 0].size < chunk_size):
        raise sd.CallbackStop()
        return
    #推入流
    outdata[:] = music_data[chunk_size*sound_chunk_idx:chunk_size*(sound_chunk_idx+1), :]
    sound_chunk_idx += 1;
    #改变buffer, 生成动画
    buffer[:] = np.abs(fft(outdata[0:1024, 0]))[:512:8]

# 动画函数
ani = FuncAnimation(fig, update, init_func=init, interval=20, blit=True)
# 动画开启
plt.show(block=False)


# 打开流
with sd.Stream(callback=callback, samplerate=sr, channels=2, blocksize=chunk_size, dtype=music_data.dtype):
    print("Enter q or Q to exit:")
    while True:
        response = input()
        if response in ('', 'q', 'Q'):
            break
