var dnn =
[
    [ "Introduction", "dnn.html#dnn_intro", null ],
    [ "Karel's DNN implementation", "dnn1.html", [
      [ "Top-level script", "dnn1.html#dnn1_toplevel_scripts", null ],
      [ "Training script internals", "dnn1.html#dnn1_training_script_internals", null ],
      [ "Training tools", "dnn1.html#dnn1_train_tools", null ],
      [ "Other tools", "dnn1.html#dnn1_manipulating_tools", null ],
      [ "Showing the network topology with nnet-info", "dnn1.html#dnn1_print_by_nnet_info", null ],
      [ "Advanced features", "dnn1.html#dnn1_advanced_features", [
        [ "Frame-weighted training", "dnn1.html#dnn1_weighted_training", null ],
        [ "Training with external targets", "dnn1.html#dnn1_external_targets", null ],
        [ "Mean-Square-Error training", "dnn1.html#dnn1_mse_training", null ],
        [ "Training with tanh", "dnn1.html#dnn1_tanh", null ],
        [ "Conversion of a DNN model between nnet1 -> nnet2", "dnn1.html#dnn1_conversion_to_dnn2", null ]
      ] ],
      [ "The C++ code", "dnn1.html#dnn1_cpp_code", [
        [ "Neural network representation", "dnn1.html#dnn1_design", null ],
        [ "Extending the network by a new component", "dnn1.html#dnn1_extending", null ]
      ] ]
    ] ],
    [ "Dan's DNN implementation", "dnn2.html", [
      [ "Introduction", "dnn2.html#dnn2_intro", null ],
      [ "Looking at the scripts", "dnn2.html#dnn2_toplevel", [
        [ "Top-level training script", "dnn2.html#dnn2_train_pnorm", null ],
        [ "Input features to the neural net.", "dnn2.html#dnn2_features", null ],
        [ "Dumping training examples to disk", "dnn2.html#dnn2_egs", null ],
        [ "Neural net initialization", "dnn2.html#dnn2_train_init", null ],
        [ "Neural net training", "dnn2.html#dnn2_train_train", null ],
        [ "Final model combination", "dnn2.html#dnn2_train_combine", null ],
        [ "Mixing-up", "dnn2.html#dnn2_mixup", null ],
        [ "Model \"shrinking\" and \"fixing\"", "dnn2.html#dnn2_fix", null ]
      ] ],
      [ "Use of GPUs or CPUs", "dnn2.html#dnn2_gpu", [
        [ "Switching between GPU and CPU use", "dnn2.html#dnn2_gpu_switching", null ],
        [ "Tuning the number of jobs", "dnn2.html#dnn2_gpu_num_jobs", null ]
      ] ],
      [ "Tuning the neural network training", "dnn2.html#dnn2_tuning", [
        [ "Number of parameters (hidden layers and hidden layer size)", "dnn2.html#dnn2_parameters", null ],
        [ "Learning rates", "dnn2.html#dnn2_learning_rate", null ],
        [ "Minibatch size", "dnn2.html#dnn2_minibatch_size", null ],
        [ "Max-change", "dnn2.html#dnn2_max_change", null ],
        [ "Number of epochs, etc.", "dnn2.html#dnn2_num_epochs", null ],
        [ "Feature splicing width.", "dnn2.html#dnn2_splice_width", null ],
        [ "Configuration values relating to the LDA transform.", "dnn2.html#dnn2_lda_config", null ],
        [ "Other miscellaneous configuration values", "dnn2.html#dnn2_misc", null ]
      ] ],
      [ "Preconditioned Stochastic Gradient Descent", "dnn2.html#dnn2_algorithms_preconditioning", null ]
    ] ],
    [ "The \"nnet3\" setup", "dnn3.html", "dnn3" ],
    [ "'Chain' models", "chain.html", [
      [ "Introduction to 'chain' models", "chain.html#chain_intro", null ],
      [ "Where to find scripts for the 'chain' models", "chain.html#chain_scripts", null ],
      [ "The chain model", "chain.html#chain_model", null ],
      [ "The training procedure for 'chain' models", "chain.html#chain_training", [
        [ "The denominator FST", "chain.html#chain_training_denominator", [
          [ "Phone language model for the denominator FST", "chain.html#chain_training_denominator_phone_lm", null ],
          [ "Compilation of the denominator FST", "chain.html#chain_training_denominator_compilation", null ],
          [ "Initial and final probabilities, and 'normalization FST'", "chain.html#chain_training_denominator_normalization", null ]
        ] ],
        [ "Numerator FSTs", "chain.html#chain_training_numerator", [
          [ "Splitting the numerator FSTs", "chain.html#chain_training_numerator_splitting", null ],
          [ "Normalizing the numerator FSTs", "chain.html#chain_training_numerator_normalization", null ],
          [ "Format of the numerator FSTs", "chain.html#chain_training_numerator_format", null ]
        ] ],
        [ "Fixed-length chunks, and minibatches", "chain.html#chain_training_splitting", null ],
        [ "Training on frame-shifted data", "chain.html#chain_training_shifting", null ],
        [ "GPU issues in training", "chain.html#chain_training_gpu", null ]
      ] ],
      [ "Decoding with 'chain' models", "chain.html#chain_decoding", null ]
    ] ]
];