#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_source_code
@File    ：process_worker.py
@Author  ：fengzhengxiong
@Date    ：2025/7/17 10:10 
'''


import subprocess
import os
import psutil
from PySide6.QtCore import QThread, Signal


class ProcessWorker(QThread):
    """
    经过强化的工作线程，专注于健壮的子进程管理。
    """
    log_message = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, command: str, work_dir: str = None):
        super().__init__()
        self.command = command
        self.work_dir = work_dir
        self.process = None
        self._is_stopped = False

    def run(self):
        self._is_stopped = False
        self.log_message.emit(f"[COMMAND] {self.command}")
        if self.work_dir:
            self.log_message.emit(f"[WORKDIR] {self.work_dir}")

        try:
            # shell=True 在Windows下对于复杂命令有时是必要的，但为了更好的进程控制，
            # 我们将命令拆分。对于你的情况 "python yolo.exe ...", shell=True 也可以
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=self.work_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # 实时读取输出
            for line in iter(self.process.stdout.readline, ''):
                if self._is_stopped:
                    # 如果标记为停止，跳出循环，进入进程清理阶段
                    break

                line = line.strip()
                if not line:
                    continue

                self.log_message.emit(line)

            # 等待进程自然结束，获取返回码
            return_code = self.process.wait()

            if self._is_stopped:
                # 如果是用户主动停止，返回特定消息
                self.finished.emit(False, "任务被用户手动终止。")
            elif return_code == 0:
                self.finished.emit(True, "任务成功完成！")
            else:
                self.finished.emit(False, f"任务异常结束，返回码: {return_code}")

        except Exception as e:
            error_msg = f"执行命令时发生严重错误: {e}"
            self.log_message.emit(f"[ERROR] {error_msg}")
            self.finished.emit(False, error_msg)
        finally:
            # 确保无论如何都尝试清理残留进程
            self._cleanup_process()

    def stop(self):
        """
        公开的停止方法，由外部调用（如点击"停止"按钮或关闭窗口）。
        它只设置一个标志，并调用内部的清理函数。
        """
        if not self._is_stopped:
            self.log_message.emit("[ACTION] 接收到停止请求...")
            self._is_stopped = True
            self._cleanup_process()

    def _cleanup_process(self):
        """
        核心的进程清理函数，使用 psutil 确保彻底终止。
        """
        # 检查 self.process 是否存在且仍在运行
        if not self.process or self.process.poll() is not None:
            return

        self.log_message.emit(f"[CLEANUP] 开始清理进程 PID: {self.process.pid}")
        try:
            # 找到父进程
            parent = psutil.Process(self.process.pid)
            # 找到并杀死所有子进程（孙子进程等）
            children = parent.children(recursive=True)
            for child in children:
                self.log_message.emit(f"[CLEANUP] 终止子进程 PID: {child.pid}")
                child.kill()

            # 最后杀死父进程本身
            self.log_message.emit(f"[CLEANUP] 终止主进程 PID: {parent.pid}")
            parent.kill()

            # 等待进程确实被终止
            parent.wait(timeout=5)
            self.log_message.emit("[CLEANUP] 进程已成功终止。")

        except psutil.NoSuchProcess:
            # 进程可能在我们操作前就已经自己结束了，这是正常情况
            self.log_message.emit("[CLEANUP] 进程已不存在，无需清理。")
        except psutil.TimeoutExpired:
            self.log_message.emit("[ERROR] 终止进程超时，可能存在僵尸进程！")
        except Exception as e:
            self.log_message.emit(f"[ERROR] 清理进程时发生错误: {e}")