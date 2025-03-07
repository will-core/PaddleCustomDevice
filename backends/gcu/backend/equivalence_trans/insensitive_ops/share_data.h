/* Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. */

#pragma once

#include <memory>
#include <string>
#include <vector>

#include "backend/register/register.h"

namespace backend {
const char *const kShareData = "share_data";

IMPLEMT_EQUIVALENCE_TRANS_FUNC(
    gcu_builder, op, map_inputs, running_mode, ShareDataEquivalenceTrans) {
  auto input = *(map_inputs["X"].at(0));
  auto out = input;

  return std::make_shared<GcuOp>(out);
}

EQUIVALENCE_TRANS_FUNC_REG(kShareData, INSENSITIVE, ShareDataEquivalenceTrans);
}  // namespace backend
