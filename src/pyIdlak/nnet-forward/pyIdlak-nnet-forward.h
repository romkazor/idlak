#include <limits>

#include "nnet/nnet-nnet.h"
#include "nnet/nnet-loss.h"
#include "nnet/nnet-pdf-prior.h"
#include "base/kaldi-common.h"
#include "util/common-utils.h"
#include "base/timer.h"

typedef struct NnetForwardOpts NnetForwardOpts;

int ForwardPass(NnetForwardOpts * opts);

struct NnetForwardOpts {
    std::string class_frame_counts = "";
    BaseFloat prior_scale = 1.0;
    BaseFloat prior_floor = 1e-10;
    std::string feature_transform = "";
    bool reverse_transform = false;
    bool no_softmax = false;
    bool apply_log = false;
    std::string use_gpu = "no";
    std::string model_filename;
    std::string feature_rspecifier;
    std::string feature_wspecifier;
};
