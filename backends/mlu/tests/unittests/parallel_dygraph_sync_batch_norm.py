# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from test_dist_base import TestParallelDyGraphRunnerBase, runtime_main

import paddle
from paddle.nn import Conv2D, SyncBatchNorm


class TestLayer(paddle.nn.Layer):
    def __init__(
        self,
        num_channels,
        num_filters,
        filter_size,
        stride=1,
        groups=1,
        act=None,
    ):
        super().__init__()

        self._conv = Conv2D(
            in_channels=num_channels,
            out_channels=num_filters,
            kernel_size=filter_size,
            stride=stride,
            padding=(filter_size - 1) // 2,
            groups=groups,
            bias_attr=False,
        )

        self._sync_batch_norm = SyncBatchNorm(num_filters)

        self._conv2 = Conv2D(
            in_channels=num_filters,
            out_channels=num_filters,
            kernel_size=filter_size,
            stride=stride,
            padding=(filter_size - 1) // 2,
            groups=groups,
            bias_attr=False,
        )

        self._sync_batch_norm2 = SyncBatchNorm(
            num_filters, weight_attr=False, bias_attr=False
        )

    def forward(self, inputs):
        y = self._conv(inputs)
        y = self._sync_batch_norm(y)
        y = self._conv2(y)
        y = self._sync_batch_norm2(y)

        return y


class TestSyncBatchNorm(TestParallelDyGraphRunnerBase):
    def get_model(self):
        model = TestLayer(1, 64, 7)
        train_reader = paddle.batch(
            paddle.dataset.mnist.test(),
            batch_size=32,
            drop_last=True,
        )
        opt = paddle.optimizer.Adam(learning_rate=1e-3, parameters=model.parameters())
        return model, train_reader, opt

    def run_one_loop(self, model, opt, data):
        batch_size = len(data)
        dy_x_data = np.array([x[0].reshape(1, 28, 28) for x in data]).astype("float32")
        img = paddle.to_tensor(dy_x_data)
        img.stop_gradient = False

        out = model(img)

        out = paddle.mean(out)

        return out


if __name__ == "__main__":
    runtime_main(TestSyncBatchNorm)
