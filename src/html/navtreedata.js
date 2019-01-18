var NAVTREE =
[
  [ "Kaldi", "index.html", [
    [ "About the Kaldi project", "about.html", [
      [ "What is Kaldi?", "about.html#about_what", null ],
      [ "The name Kaldi", "about.html#about_name", null ],
      [ "Kaldi's versus other toolkits", "about.html#about_compare", null ],
      [ "The flavor of Kaldi", "about.html#about_flavor", null ],
      [ "Status of the project", "about.html#about_status", null ],
      [ "Referencing Kaldi in papers", "about.html#about_reference", null ]
    ] ],
    [ "Other Kaldi-related resources (and how to get help)", "other.html", null ],
    [ "Downloading and installing Kaldi", "install.html", [
      [ "Dowloading Kaldi", "install.html#install_download", null ],
      [ "Installing Kaldi", "install.html#install_install", null ]
    ] ],
    [ "Versions of Kaldi", "versions.html", [
      [ "Versioning scheme", "versions.html#versions_scheme", null ],
      [ "Versions (and changes)", "versions.html#versions_versions", [
        [ "Version 5.0", "versions.html#versions_versions_50", null ],
        [ "Version 5.1", "versions.html#versions_versions_51", null ],
        [ "Version 5.2", "versions.html#versions_versions_52", null ],
        [ "Version 5.3", "versions.html#versions_versions_53", null ],
        [ "Version 5.4", "versions.html#versions_versions_54", null ],
        [ "Version 5.5", "versions.html#versions_versions_55", null ]
      ] ]
    ] ],
    [ "Software required to install and run Kaldi", "dependencies.html", [
      [ "Ideal computing environment", "dependencies.html#dependencies_environment", null ],
      [ "Bare minimum computing environment", "dependencies.html#dependencies_minimum", null ],
      [ "Software packages required", "dependencies.html#dependencies_packages", null ],
      [ "Software packages installed by Kaldi", "dependencies.html#dependencies_installed", null ]
    ] ],
    [ "Legal stuff", "legal.html", null ],
    [ "Kaldi tutorial", "tutorial.html", "tutorial" ],
    [ "Kaldi for Dummies tutorial", "kaldi_for_dummies.html", [
      [ "Introduction", "kaldi_for_dummies.html#kaldi_for_dummies_introduction", null ],
      [ "Environment", "kaldi_for_dummies.html#kaldi_for_dummies_environment", null ],
      [ "Download Kaldi", "kaldi_for_dummies.html#kaldi_for_dummies_download", null ],
      [ "Kaldi directories structure", "kaldi_for_dummies.html#kaldi_for_dummies_directories", null ],
      [ "Your exemplary project", "kaldi_for_dummies.html#kaldi_for_dummies_project", null ],
      [ "Data preparation", "kaldi_for_dummies.html#kaldi_for_dummies_data", [
        [ "Audio data", "kaldi_for_dummies.html#kaldi_for_dummies_audio", null ],
        [ "Acoustic data", "kaldi_for_dummies.html#kaldi_for_dummies_acoustic", null ],
        [ "Language data", "kaldi_for_dummies.html#kaldi_for_dummies_language", null ]
      ] ],
      [ "Project finalization", "kaldi_for_dummies.html#kaldi_for_dummies_finalization", [
        [ "Tools attachment", "kaldi_for_dummies.html#kaldi_for_dummies_tools", null ],
        [ "Scoring script", "kaldi_for_dummies.html#kaldi_for_dummies_scoring", null ],
        [ "SRILM installation", "kaldi_for_dummies.html#kaldi_for_dummies_srilm", null ],
        [ "Configuration files", "kaldi_for_dummies.html#kaldi_for_dummies_configuration", null ]
      ] ],
      [ "Running scripts creation", "kaldi_for_dummies.html#kaldi_for_dummies_running", null ],
      [ "Getting results", "kaldi_for_dummies.html#kaldi_for_dummies_results", null ],
      [ "Summary", "kaldi_for_dummies.html#kaldi_for_dummies_summary", null ]
    ] ],
    [ "Examples included with Kaldi", "examples.html", null ],
    [ "Glossary of terms", "glossary.html", null ],
    [ "Data preparation", "data_prep.html", [
      [ "Introduction", "data_prep.html#data_prep_intro", null ],
      [ "Data preparation-- the \"data\" part.", "data_prep.html#data_prep_data", [
        [ "Files you need to create yourself", "data_prep.html#data_prep_data_yourself", null ],
        [ "Files you don't need to create yourself", "data_prep.html#data_prep_data_noneed", null ]
      ] ],
      [ "Data preparation-- the \"lang\" directory.", "data_prep.html#data_prep_lang", null ],
      [ "Contents of the \"lang\" directory", "data_prep.html#data_prep_lang_contents", null ],
      [ "Creating the \"lang\" directory", "data_prep.html#data_prep_lang_creating", null ],
      [ "Creating the language model or grammar", "data_prep.html#data_prep_grammar", null ]
    ] ],
    [ "The build process (how Kaldi is compiled)", "build_setup.html", [
      [ "Build process on Windows", "build_setup.html#build_setup_windows", null ],
      [ "How our configure script works (for UNIX variants)", "build_setup.html#build_setup_configure", null ],
      [ "Editing kaldi.mk", "build_setup.html#build_setup_editing", null ],
      [ "Targets defined by the Makefiles", "build_setup.html#build_setup_targets", null ],
      [ "Where do the compiled binaries go?", "build_setup.html#build_setup_output", null ],
      [ "How our Makefiles work", "build_setup.html#build_setup_make", null ],
      [ "Which platforms has Kaldi been compiled on?", "build_setup.html#build_setup_platforms", null ]
    ] ],
    [ "The Kaldi coding style", "style.html", null ],
    [ "History of the Kaldi project", "history.html", [
      [ "Acknowledgements", "history.html#history_ack", null ]
    ] ],
    [ "The Kaldi Matrix library", "matrix.html", [
      [ "Matrix and vector types", "matrix.html#matrix_sec_types", null ],
      [ "Symmetric and triangular matrices", "matrix.html#matrix_sec_sym", null ],
      [ "Sub-vectors and sub-matrices.", "matrix.html#matrix_sec_sub", null ],
      [ "Calling conventions for vectors and matrices", "matrix.html#matrix_sec_calling", null ],
      [ "Copying matrix and vector types", "matrix.html#matrix_sec_copy", null ],
      [ "Scalar products", "matrix.html#matrix_sec_scalar", null ],
      [ "Resizing", "matrix.html#matric_sec_resizing", null ],
      [ "Matrix I/O", "matrix.html#matrix_sec_io", null ],
      [ "Other matrix library functions", "matrix.html#matrix_sec_other", null ]
    ] ],
    [ "External matrix libraries", "matrixwrap.html", [
      [ "Overview", "matrixwrap.html#matrixwrap_summary", null ],
      [ "Basic Linear Algebra Subroutines (BLAS)", "matrixwrap.html#matrixwrap_blas", null ],
      [ "Linear Algebra PACKage (LAPACK)", "matrixwrap.html#matrixwrap_lapack", null ],
      [ "Automatically Tuned Linear Algebra Software (ATLAS)", "matrixwrap.html#matrixwrap_atlas", [
        [ "Installing ATLAS (on Windows)", "matrixwrap.html#matrixwrap_atlas_install_windows", null ],
        [ "Installing ATLAS (on Linux)", "matrixwrap.html#matrixwrap_atlas_install_linux", null ]
      ] ],
      [ "Intel Math Kernel Library (MKL)", "matrixwrap.html#matrixwrap_mkl", null ],
      [ "OpenBLAS", "matrixwrap.html#matrixwrap_openblas", null ],
      [ "Java Matrix Package (JAMA)", "matrixwrap.html#matrixwrap_jama", null ],
      [ "Linking errors you might encounter", "matrixwrap.html#matrixwrap_linking_errors", [
        [ "f2c or g2c errors", "matrixwrap.html#matrix_err_f2c", null ],
        [ "CLAPACK linking errors", "matrixwrap.html#matrix_err_clapack", null ],
        [ "BLAS linking errors", "matrixwrap.html#matrix_err_blas", null ],
        [ "cblaswrap linking errors", "matrixwrap.html#matrix_err_cblaswrap", null ],
        [ "Missing the ATLAS implementation of BLAS", "matrixwrap.html#matrix_err_atl_blas", null ],
        [ "Missing the ATLAS implementation of (parts of) CLAPACK", "matrixwrap.html#matrix_err_atl_clapack", null ]
      ] ]
    ] ],
    [ "The CUDA Matrix library", "cudamatrix.html", null ],
    [ "Kaldi I/O mechanisms", "io.html", "io" ],
    [ "Kaldi I/O from a command-line perspective.", "io_tut.html", [
      [ "Overview", "io_tut.html#Overview", [
        [ "Non-table I/O", "io_tut.html#io_tut_nontable", null ],
        [ "Table I/O", "io_tut.html#io_tut_table", [
          [ "Table I/O (with ranges)", "io_tut.html#io_tut_table_ranges", null ]
        ] ],
        [ "Utterance-to-speaker and speaker-to-utterance maps.", "io_tut.html#io_tut_maps", null ]
      ] ]
    ] ],
    [ "Kaldi logging and error-reporting", "error.html", [
      [ "Overview", "error.html#error_overview", null ],
      [ "Assertions in Kaldi", "error.html#error_assertions", null ],
      [ "Exceptions thrown by KALDI_ERR", "error.html#error_exceptions", null ],
      [ "Compile-time assertions in Kaldi", "error.html#error_compile_time_assertions", null ]
    ] ],
    [ "Parsing command-line options", "parse_options.html", [
      [ "Introduction", "parse_options.html#parse_options_introduction", null ],
      [ "Example of parsing command-line options", "parse_options.html#parse_options_example", null ],
      [ "Implicit command-line arguments", "parse_options.html#parse_options_implicit", null ]
    ] ],
    [ "Other Kaldi utilities", "util.html", [
      [ "Text utilities", "util.html#util_sec_text", null ],
      [ "STL utilities", "util.html#util_sec_stl", null ],
      [ "Math utilities", "util.html#util_sec_math", null ],
      [ "Other utilities", "util.html#util_sec_other", null ]
    ] ],
    [ "Clustering mechanisms in Kaldi", "clustering.html", [
      [ "The Clusterable interface", "clustering.html#clustering_sec_intro", null ],
      [ "Clustering algorithms", "clustering.html#clustering_sec_algo", [
        [ "K-means and algorithms with similar interfaces", "clustering.html#clustering_sec_kmeans", null ],
        [ "Tree clustering algorithm", "clustering.html#clustering_sec_tree_cluster", null ]
      ] ]
    ] ],
    [ "HMM topology and transition modeling", "hmm.html", [
      [ "Introduction", "hmm.html#hmm_intro", null ],
      [ "HMM topologies", "hmm.html#hmm_topology", null ],
      [ "Pdf-classes", "hmm.html#pdf_class", null ],
      [ "Transition models (the TransitionModel object)", "hmm.html#transition_model", [
        [ "How we model transition probabilities in Kaldi", "hmm.html#transition_model_how", null ],
        [ "The reason for transition-ids etc.", "hmm.html#transition_model_mappings", null ],
        [ "Integer identifiers used by TransitionModel", "hmm.html#transition_model_identifiers", null ]
      ] ],
      [ "Training the transition model", "hmm.html#hmm_transition_training", null ],
      [ "Alignments in Kaldi", "hmm.html#hmm_alignment", null ],
      [ "State-level posteriors", "hmm.html#hmm_post", null ],
      [ "Gaussian-level posteriors", "hmm.html#hmm_gpost", null ],
      [ "Functions for converting HMMs to FSTs", "hmm.html#hmm_graph", [
        [ "GetHTransducer()", "hmm.html#hmm_graph_get_h_transducer", null ],
        [ "The HTransducerConfig configuration class", "hmm.html#hmm_graph_config", null ],
        [ "The function GetHmmAsFst()", "hmm.html#hmm_graph_get_hmm_as_fst", null ],
        [ "AddSelfLoops()", "hmm.html#hmm_graph_add_self_loops", null ],
        [ "Adding transition probabilities to FSTs", "hmm.html#hmm_graph_add_transition_probs", null ]
      ] ],
      [ "Reordering transitions", "hmm.html#hmm_reorder", null ],
      [ "Scaling of transition and acoustic probabilities", "hmm.html#hmm_scale", null ]
    ] ],
    [ "Decision tree internals", "tree_internals.html", [
      [ "Event maps", "tree_internals.html#treei_event_map", null ],
      [ "Statistics for building the tree", "tree_internals.html#treei_stats", null ],
      [ "Classes and functions involved in tree-building", "tree_internals.html#treei_func", [
        [ "Questions (config class)", "tree_internals.html#treei_func_questions", null ],
        [ "Lowest-level functions", "tree_internals.html#treei_func_low", null ],
        [ "Intermediate-level functions", "tree_internals.html#treei_func_intermediate", null ],
        [ "Top-level tree-building functions", "tree_internals.html#treei_func_top", null ]
      ] ]
    ] ],
    [ "How decision trees are used in Kaldi", "tree_externals.html", [
      [ "Introduction", "tree_externals.html#tree_intro", null ],
      [ "Phonetic context windows", "tree_externals.html#tree_window", null ],
      [ "The tree building process", "tree_externals.html#tree_building", null ],
      [ "PDF identifiers", "tree_externals.html#pdf_id", null ],
      [ "Context dependency objects", "tree_externals.html#tree_ctxdep", null ],
      [ "An example of a decision tree", "tree_externals.html#tree_example", null ],
      [ "The ilabel_info object", "tree_externals.html#tree_ilabel", null ]
    ] ],
    [ "Decoding graph construction in Kaldi", "graph.html", [
      [ "Overview of graph creation", "graph.html#graph_overview", null ],
      [ "Disambiguation symbols", "graph.html#graph_disambig", null ],
      [ "The ContextFst object", "graph.html#graph_context", null ],
      [ "Avoiding weight pushing", "graph.html#graph_weight", null ]
    ] ],
    [ "Decoding-graph creation recipe (test time)", "graph_recipe_test.html", [
      [ "Preparing the initial symbol tables", "graph_recipe_test.html#graph_symtab", null ],
      [ "Preparing the lexicon L", "graph_recipe_test.html#graph_lexicon", null ],
      [ "Preparing the grammar G", "graph_recipe_test.html#graph_grammar", null ],
      [ "Preparing LG", "graph_recipe_test.html#graph_lg", null ],
      [ "Preparing CLG", "graph_recipe_test.html#graph_clg", [
        [ "Making the context transducer", "graph_recipe_test.html#graph_c", null ],
        [ "Composing with C dynamically", "graph_recipe_test.html#graph_compose_c", null ],
        [ "Reducing the number of context-dependent input symbols", "graph_recipe_test.html#graph_change_ilabel", null ]
      ] ],
      [ "Making the H transducer", "graph_recipe_test.html#graph_h", null ],
      [ "Making HCLG", "graph_recipe_test.html#graph_hclg", null ],
      [ "Adding self-loops to HCLG", "graph_recipe_test.html#graph_selfloops", null ]
    ] ],
    [ "Decoding-graph creation recipe (training time)", "graph_recipe_train.html", [
      [ "Command-line programs involved in decoding-graph creation", "graph_recipe_train.html#graph_recipe_command", null ],
      [ "Internals of graph creation", "graph_recipe_train.html#graph_recipe_internal", null ]
    ] ],
    [ "Support for grammars and graphs with on-the-fly parts.", "grammar.html", [
      [ "Relation to OpenFst's 'Replace()' operation", "grammar.html#grammar_replace", [
        [ "Overview of the framework", "grammar.html#grammar_overview", null ]
      ] ],
      [ "Symbol tables and special symbols", "grammar.html#grammar_symtabs", null ],
      [ "Special symbols in G.fst", "grammar.html#grammar_special_g", null ],
      [ "Special symbols in LG.fst", "grammar.html#grammar_special_lg", [
        [ "Special symbols in L.fst", "grammar.html#grammar_special_l", null ]
      ] ],
      [ "Special symbols in CLG.fst", "grammar.html#grammar_special_clg", [
        [ "Special symbols in C.fst", "grammar.html#grammar_special_c", null ]
      ] ],
      [ "Special symbols in HCLG.fst", "grammar.html#grammar_special_hclg", [
        [ "Special symbols in H.fst", "grammar.html#grammar_special_h", null ]
      ] ],
      [ "The decoder", "grammar.html#grammar_decoder", [
        [ "The ArcIterator of GrammarFst", "grammar.html#grammar_decoder_arc_iterator", null ]
      ] ],
      [ "Preparing FSTs for use in grammar decoding", "grammar.html#grammar_prepare", null ],
      [ "Output labels in GrammarFsts", "grammar.html#grammar_olabels", null ]
    ] ],
    [ "Finite State Transducer algorithms", "fst_algo.html", [
      [ "Determinization", "fst_algo.html#fst_algo_det", [
        [ "Debugging determinization", "fst_algo.html#fst_algo_det_debug", null ],
        [ "Determinization in the log semiring", "fst_algo.html#fst_algo_det_log", null ]
      ] ],
      [ "Removing epsilons", "fst_algo.html#fst_algo_eps", null ],
      [ "Preserving stochasticity and testing it", "fst_algo.html#fst_algo_stochastic", null ],
      [ "Minimization", "fst_algo.html#fst_algo_minimization", null ],
      [ "Composition", "fst_algo.html#fst_algo_composition", null ],
      [ "Adding and removing disambiguation symbols", "fst_algo.html#fst_algo_disambig", null ]
    ] ],
    [ "Decoders used in the Kaldi toolkit", "decoders.html", [
      [ "The Decodable interface", "decoders.html#decodable_interface", null ],
      [ "SimpleDecoder: the simplest possible decoder", "decoders.html#decoders_simple", [
        [ "Interface of SimpleDecoder", "decoders.html#decoders_simple_itf", null ],
        [ "How SimpleDecoder works", "decoders.html#decoders_simple_workings", null ]
      ] ],
      [ "FasterDecoder: a more optimized decoder", "decoders.html#decoders_faster", null ],
      [ "BiglmDecoder: decoding with large language models.", "decoders.html#decoders_biglm", null ],
      [ "Lattice generating decoders", "decoders.html#decoders_lattice", null ]
    ] ],
    [ "Lattices in Kaldi", "lattices.html", [
      [ "Introduction", "lattices.html#lattices_intro", null ],
      [ "The Lattice type", "lattices.html#lattices_lattice", null ],
      [ "Compact lattices (the CompactLattice type)", "lattices.html#lattices_compact", null ],
      [ "Lattice generation", "lattices.html#lattices_generation", [
        [ "Getting the raw lattice, and converting it into the final form.", "lattices.html#lattices_generation_raw", null ]
      ] ],
      [ "Lattices in archives", "lattices.html#lattices_archives", null ],
      [ "Operations on lattices", "lattices.html#lattices_operations", [
        [ "Pruning lattices", "lattices.html#lattices_operations_pruning", null ],
        [ "Computing the best path through a lattice", "lattices.html#lattices_operations_best_path", null ],
        [ "Computing the N-best hypotheses", "lattices.html#lattices_operations_nbest", null ],
        [ "Language model rescoring", "lattices.html#lattices_operations_lmrescore", null ],
        [ "Probability scaling", "lattices.html#lattices_operations_scale", null ],
        [ "Lattice union", "lattices.html#lattices_union", null ],
        [ "Lattice composition", "lattices.html#lattices_operations_compose", null ],
        [ "Lattice interpolation", "lattices.html#lattices_operations_interp", null ],
        [ "Conversion of lattices to phones", "lattices.html#lattices_operations_phones", null ],
        [ "Lattice projection", "lattices.html#lattices_operations_project", null ],
        [ "Lattice equivalence testing", "lattices.html#lattices_operations_equivalent", null ],
        [ "Removing alignments from lattices", "lattices.html#lattices_operations_rmali", null ],
        [ "Error boosting in lattices", "lattices.html#lattices_operations_boost", null ],
        [ "Computing posteriors from lattices", "lattices.html#lattices_operations_post", null ],
        [ "Determinization of lattices", "lattices.html#lattices_operations_det", null ],
        [ "Computing oracle WERs from lattices", "lattices.html#lattices_operations_oracle", null ],
        [ "Adding transition probabilities to lattices", "lattices.html#lattices_operations_tprob", null ],
        [ "Converting lattices to FSTs", "lattices.html#lattices_operations_to_fst", null ],
        [ "Copying lattices", "lattices.html#lattices_operations_copy", null ]
      ] ],
      [ "N-best lists and best paths", "lattices.html#lattice_nbest", null ],
      [ "Times on lattices", "lattices.html#lattices_times", null ]
    ] ],
    [ "Acoustic modeling code", "model.html", [
      [ "Introduction", "model.html#model_intro", null ],
      [ "Diagonal GMMs", "model.html#model_diag", [
        [ "Individual GMMs", "model.html#model_diag_gmm", null ],
        [ "GMM-based acoustic model", "model.html#model_diag_am", null ],
        [ "Full-covariance GMMs", "model.html#model_full_gmm", null ]
      ] ],
      [ "Subspace Gaussian Mixture Models (SGMMs)", "model.html#model_sgmm", null ]
    ] ],
    [ "Feature extraction", "feat.html", [
      [ "Introduction", "feat.html#feat_intro", null ],
      [ "Computing MFCC features", "feat.html#feat_mfcc", null ],
      [ "Computing PLP features", "feat.html#feat_plp", null ],
      [ "Feature-level Vocal Tract Length Normalization (VTLN).", "feat.html#feat_vtln", null ]
    ] ],
    [ "Feature and model-space transforms in Kaldi", "transform.html", [
      [ "Introduction", "transform.html#transform_intro", null ],
      [ "Applying global linear or affine feature transforms", "transform.html#transform_apply", null ],
      [ "Speaker-independent versus per-speaker versus per-utterance adaptation", "transform.html#transform_perspk", null ],
      [ "Utterance-to-speaker and speaker-to-utterance maps", "transform.html#transform_utt2spk", null ],
      [ "Composing transforms", "transform.html#transform_compose", null ],
      [ "Silence weighting when estimating transforms", "transform.html#transform_weight", null ],
      [ "Linear Discriminant Analysis (LDA) transforms", "transform.html#transform_lda", null ],
      [ "Frame splicing", "transform.html#transform_splice", null ],
      [ "Delta feature computation", "transform.html#transform_delta", null ],
      [ "Heteroscedastic Linear Discriminant Analysis (HLDA)", "transform.html#transform_hlda", null ],
      [ "Global Semi-tied Covariance (STC) / Maximum Likelihood Linear Transform (MLLT) estimation", "transform.html#transform_mllt", null ],
      [ "Global CMLLR/fMLLR transforms", "transform.html#transform_cmllr_global", null ],
      [ "Linear VTLN (LVTLN)", "transform.html#transform_lvtln", null ],
      [ "Exponential Transform (ET)", "transform.html#transform_et", null ],
      [ "Cepstral mean and variance normalization", "transform.html#transform_cmvn", null ],
      [ "Building regression trees for adaptation", "transform.html#transform_regtree", null ]
    ] ],
    [ "Deep Neural Networks in Kaldi", "dnn.html", "dnn" ],
    [ "Online decoding in Kaldi", "online_decoding.html", "online_decoding" ],
    [ "Keyword Search in Kaldi", "kws.html", [
      [ "Introduction", "kws.html#kws_intro", null ],
      [ "Typical Kaldi KWS system", "kws.html#kws_system", null ],
      [ "Proxy keywords", "kws.html#kws_proxy", null ],
      [ "Babel scripts", "kws.html#kws_scripts", [
        [ "A highlevel look", "kws.html#kws_scripts_highlevel", null ],
        [ "Prepare KWS data", "kws.html#kws_scripts_dataprep", null ],
        [ "Indexing and searching", "kws.html#kws_scripts_index_and_search", null ]
      ] ]
    ] ],
    [ "Parallelization in Kaldi", "queue.html", [
      [ "Introduction", "queue.html#parallelization_intro", null ],
      [ "Common interface of parallelization tools", "queue.html#parallelization_common", [
        [ "New-style options (unified interface)", "queue.html#parallelization_common_new", null ],
        [ "Example of configuring grid software with new-style options", "queue.html#parallelization_common_new_example", null ]
      ] ],
      [ "Parallelization using specific scripts", "queue.html#parallelization_specific", [
        [ "Parallelization using queue.pl", "queue.html#parallelization_specific_queue", null ],
        [ "Parallelization using run.pl", "queue.html#parallelization_specific_run", null ],
        [ "Parallelization using ssh.pl", "queue.html#parallelization_specific_ssh", null ],
        [ "Parallelization using slurm.pl", "queue.html#parallelization_specific_slurm", null ]
      ] ],
      [ "Setting up GridEngine for use with Kaldi", "queue.html#parallelization_gridengine", [
        [ "Installing GridEngine", "queue.html#parallelization_gridengine_installing", null ],
        [ "Configuring GridEngine", "queue.html#parallelization_gridengine_configuring", null ],
        [ "Configuring GridEngine (advanced)", "queue.html#parallelization_gridengine_configuring_advanced", null ],
        [ "Configuring GridEngine (adding nodes)", "queue.html#parallelization_gridengine_configuring_adding", null ]
      ] ],
      [ "Keeping your grid stable", "queue.html#parallelization_grid_stable", [
        [ "Keeping your grid stable (OOM)", "queue.html#parallelization_grid_stable_oom", null ],
        [ "Keeping your grid stable (NFS)", "queue.html#parallelization_grid_stable_nfs", null ],
        [ "Keeping your grid stable (general issues)", "queue.html#parallelization_grid_stable_misc", null ]
      ] ]
    ] ],
    [ "About the Idlak system", "idlak.html", [
      [ "What is Idlak?", "idlak.html#idlak_what", null ],
      [ "Installation", "idlak.html#idlak_install", null ]
    ] ],
    [ "The Idlak context extraction system", "idlakcex.html", [
      [ "Introduction", "idlakcex.html#idlakcex_intro", null ],
      [ "Context Architecture", "idlakcex.html#idlakcex_archi", null ],
      [ "Context Extraction", "idlakcex.html#idlaxcex_extraction", null ],
      [ "Question Architecture", "idlakcex.html#idlakcex_qarchi", null ],
      [ "Adding Context Extraction Functions", "idlakcex.html#idlakcex_addcex", null ],
      [ "Adding Context Questions", "idlakcex.html#idlakcex_addqst", null ]
    ] ],
    [ "Testing the Idlak Front End with HTS", "idlakhtstest.html", [
      [ "Introduction", "idlakhtstest.html#idlaktxp_intro", null ],
      [ "Downloading HTS", "idlakhtstest.html#idlaktxp_downloadhts", null ],
      [ "Downloading Arctic STL data", "idlakhtstest.html#idlaktxp_arcticstl", null ],
      [ "Building Full Context Models", "idlakhtstest.html#idlaktxp_buikldcex", null ],
      [ "Integrating KALDI CEX output with HTS", "idlakhtstest.html#idlaktxp_htsintegration", null ],
      [ "Creating Models for Speech Generation", "idlakhtstest.html#idlaktxp_htsgeneration", null ],
      [ "HTS training", "idlakhtstest.html#idlaktxp_htstraining", null ]
    ] ],
    [ "The Idlak text processing system", "idlaktxp.html", [
      [ "Architecture", "idlaktxp.html#idlaktxp_archi", null ],
      [ "Voice Data", "idlaktxp.html#idlaktxp_voice_data", null ],
      [ "XML tagset", "idlaktxp.html#idlaktxp_XML_tagset", null ],
      [ "Description of Modules", "idlaktxp.html#idlaktxp_description_modules", [
        [ "Tokenisation", "idlaktxp.html#idlaktxp_token", null ],
        [ "Normalisation", "idlaktxp.html#idlaktxp_norm", null ],
        [ "Pause Insertion", "idlaktxp.html#idlaktxp_pause_insertion", null ],
        [ "Part of Speech Tagging", "idlaktxp.html#idlaktxp_pos", null ],
        [ "Phrasing", "idlaktxp.html#idlaktxp_phrase", null ],
        [ "Pronunciation", "idlaktxp.html#idlaktxp_pron", null ],
        [ "Syllabification", "idlaktxp.html#idlaktxp_syll", null ]
      ] ]
    ] ],
    [ "A Walk through the Idlak System", "idlakwalkthru.html", [
      [ "Introduction", "idlakwalkthru.html#idlakwalkthru_intro", null ],
      [ "Idlak Text Processing Front End", "idlakwalkthru.html#idlakwalkthru_idlaktxp", null ],
      [ "Idlak Full Context Extraction", "idlakwalkthru.html#idlakwalkthru_idlakcex", null ],
      [ "Voice Building: Aligner", "idlakwalkthru.html#idlakwalkthru_vbalign", null ]
    ] ],
    [ "Todo List", "todo.html", null ],
    [ "Modules", "modules.html", "modules" ],
    [ "Namespaces", null, [
      [ "Namespace List", "namespaces.html", "namespaces" ],
      [ "Namespace Members", "namespacemembers.html", [
        [ "All", "namespacemembers.html", "namespacemembers_dup" ],
        [ "Functions", "namespacemembers_func.html", "namespacemembers_func" ],
        [ "Variables", "namespacemembers_vars.html", null ],
        [ "Typedefs", "namespacemembers_type.html", "namespacemembers_type" ],
        [ "Enumerations", "namespacemembers_enum.html", null ],
        [ "Enumerator", "namespacemembers_eval.html", null ]
      ] ]
    ] ],
    [ "Classes", "annotated.html", [
      [ "Class List", "annotated.html", "annotated_dup" ],
      [ "Class Index", "classes.html", null ],
      [ "Class Hierarchy", "hierarchy.html", "hierarchy" ],
      [ "Class Members", "functions.html", [
        [ "All", "functions.html", "functions_dup" ],
        [ "Functions", "functions_func.html", "functions_func" ],
        [ "Variables", "functions_vars.html", "functions_vars" ],
        [ "Typedefs", "functions_type.html", "functions_type" ],
        [ "Enumerations", "functions_enum.html", null ],
        [ "Enumerator", "functions_eval.html", null ],
        [ "Related Functions", "functions_rela.html", null ]
      ] ]
    ] ],
    [ "Files", null, [
      [ "File List", "files.html", "files" ],
      [ "File Members", "globals.html", [
        [ "All", "globals.html", "globals_dup" ],
        [ "Functions", "globals_func.html", "globals_func" ],
        [ "Variables", "globals_vars.html", null ],
        [ "Typedefs", "globals_type.html", null ],
        [ "Macros", "globals_defs.html", null ]
      ] ]
    ] ]
  ] ]
];

var NAVTREEINDEX =
[
"_2nnet-component-test_8cc.html",
"apply-minmax_8cc_source.html",
"cblas-wrappers_8h.html#ab840cf2fc159e57ef946dd96804d2969",
"classfst_1_1DeterminizerStar.html",
"classfst_1_1LatticeDeterminizerPruned.html#a4be7351d647b91c505af9aeb2c01c54d",
"classfst_1_1StdToLatticeMapper.html#a7c15be627f6cc23313815fe7beab29e6",
"classkaldi_1_1AccumulateMultiThreadedClass.html",
"classkaldi_1_1BasicVectorHolder.html#a5d08d07b4a18a5c8e597678e213d438c",
"classkaldi_1_1ConstArpaLm.html#af96313269530658c43f53e4ac9a9944f",
"classkaldi_1_1CuMatrixBase.html#a0dcb1f41ec37f0a92007a949f3a2044f",
"classkaldi_1_1CuSparseMatrix.html#a961cf693bb50620c440ba546c0a110cf",
"classkaldi_1_1DecodableAmSgmm2.html#a335d171e311d3e2f8a67c59978bbf5a0",
"classkaldi_1_1EigenvalueDecomposition.html#af217ea89321bf41768d143de07c2b6a2",
"classkaldi_1_1FullGmm.html#aa3b124f78014405a43c4b799a96bed97",
"classkaldi_1_1IvectorExtractorStats.html#a82645d7ce6b6ada4f43d568a65d7fb6c",
"classkaldi_1_1LatticeLexiconWordAligner_1_1ComputationState.html#a43112282121c619d98acd46f059f0f7c",
"classkaldi_1_1MatrixBase.html#a0a84f475aab046afea2b9b8bf2fcd26c",
"classkaldi_1_1MleAmSgmm2Accs.html#aa710bc48bb155b286e3aa253546ea7b9",
"classkaldi_1_1OnlinePitchFeatureImpl.html#a145a2a9ef62123289bd18524cf6a19ac",
"classkaldi_1_1PipeOutputImpl.html#a3648ad4aad235f59378f9d639ac56e0a",
"classkaldi_1_1RandomAccessTableReaderScriptImpl.html#ac093fa68ea7efbb7846dabd5c37da6c2",
"classkaldi_1_1SequentialTableReaderBackgroundImpl.html#af1427fc5208b9da0df501f35fc9bb5ce",
"classkaldi_1_1SparseVector.html#a0c8fb5b8c4ad0b0950d032b74826bcba",
"classkaldi_1_1TokenVectorHolder.html#a56018b9fe9b976779cc8a7bcc0d3be91",
"classkaldi_1_1TxpLexicon.html#a8b5e4d005836401f1f877feee8ba9c9c",
"classkaldi_1_1TxpXmlData.html#a866941beb0cba0cdd0d15994a4860a52",
"classkaldi_1_1WordAlignedLatticeTester.html#a347d459bcddb295ddc12adc5660c66f5",
"classkaldi_1_1nnet1_1_1Convolutional2DComponent.html#a4c7ab412d02c039a00011bd5e31fc921",
"classkaldi_1_1nnet1_1_1MaxPooling2DComponent.html#a5f6bd333e90fc68c7e54f98a43057d32",
"classkaldi_1_1nnet1_1_1RecurrentComponent.html#a747052379bebd3e0711d77def8e01b6e",
"classkaldi_1_1nnet2_1_1AffineComponentPreconditioned.html#a93cbd3cf93a0fed1d868a35ad4a32b24",
"classkaldi_1_1nnet2_1_1DiscriminativeExampleSplitter.html#a34c4cfd2d2ae4ce76b59a55ec62a33e4",
"classkaldi_1_1nnet2_1_1Nnet.html#a45ee57254393a7d76f1108aa56086681",
"classkaldi_1_1nnet2_1_1OnlinePreconditionerSimple.html#af679b81005104cca1fc03ef8ee3b36d0",
"classkaldi_1_1nnet3_1_1AffineComponent.html#ae039d08b8ecdf570b25cecf392608866",
"classkaldi_1_1nnet3_1_1Compiler.html#a6e16f71721f026c39566bf601a91ae9d",
"classkaldi_1_1nnet3_1_1ComputationStepsComputer.html#ab1ba98152caee70149eecf30d58fb975",
"classkaldi_1_1nnet3_1_1DecodableNnetSimpleLooped.html#a8b7e28eb0bdb472bbaa0dec5ac489c52",
"classkaldi_1_1nnet3_1_1FixedScaleComponent.html#a323155ad8034c0b14762dd78ae4415b5",
"classkaldi_1_1nnet3_1_1NaturalGradientPerElementScaleComponent.html#ace20f0be9f7cc3039024159b6ee7cc13",
"classkaldi_1_1nnet3_1_1NonlinearComponent.html#a01d20602584878a6a42034cb173e14df",
"classkaldi_1_1nnet3_1_1RepeatedAffineComponent.html#a041a0abedde66a66f7ba7ea329ec3073",
"classkaldi_1_1nnet3_1_1StatisticsPoolingComponent.html#ac9e95681648792d19373aeea095bda2b",
"classkaldi_1_1nnet3_1_1UtteranceSplitter.html#ac301d3a82e1090cde05202c010ad5252",
"compressed-matrix_8cc_source.html",
"cu-array-test_8cc.html",
"cu-matrix-test_8cc.html#a90070b10015a5332f9dca5f66b96e54b",
"cu-vector-test_8cc.html#a7bd07036f81a1ca63cba0fd211f44435",
"dir_70093cb3a9d1f8840af4e997fde867c3.html",
"event-map-test_8cc.html#ae66f6b31b5ad750f1fe042a706a4e3d4",
"fmllr-diag-gmm-test_8cc.html#a9c77b4b8312b55fefd62fbc539e44cec",
"fsts-project_8cc.html",
"gmm-decode-faster-regtree-mllr_8cc.html#a0ddf1224851353fc92bfbff6f499fa97",
"group__DiagGmm.html#ga005518e528ce2f81052d3b3587912624",
"group__matrix__funcs__misc.html#ga9a7751d719e4366383f522974fbe5893",
"group__tree__group__lower.html#ga67ec2120dcbb04a78e0dc751f6b57dc6",
"io-funcs_8h.html",
"kaldi-io_8h.html#gga5fc772c800c3d40d2b95564e8a839babac3c16c315ea1f37723f6e3d5f3f09237",
"kaldi-utils_8h.html#a4ef17c6fd763d52b9f8cd2f7b6f230b9",
"lattice-interp_8cc.html",
"make-fullctx-ali_8cc_source.html",
"matrix.html#matrix_sec_calling",
"model.html#model_full_gmm",
"nnet-chain-example_8h.html#ae01be70ef8559aef9dd5a01a4028198c",
"nnet-copy_8cc_source.html",
"nnet-optimize-test_8cc.html#a8871c28ddb5af8735abd397019ba409d",
"nnet-test-utils_8cc.html#afb5a70eadfcda218c3833859bf7ceb27",
"nnet3-combine_8cc.html#a11f61b746e0773ae070094b9baa1b815",
"pitch-functions-test_8cc.html#a44ee745a24f3a6418741de6d6b32f825",
"regtree-fmllr-diag-gmm-test_8cc.html#acdb961adeb8cf4315fc06ac92ba9ae05",
"sparse-matrix-test_8cc.html#a8653cb5467c5bcb3319fee3f1419613d",
"structfst_1_1TableComposeCache.html#ad6aec6bb819bba8bac09030054ae3e10",
"structkaldi_1_1FmllrDiagGmmAccs_1_1SingleFrameStats.html#a47e90a7a9e14361ffb6033cfa1e18393",
"structkaldi_1_1LbfgsOptions.html#a5c8cf12cca09c232c34c197aa2ebb24e",
"structkaldi_1_1PlpOptions.html#aa1c183cd4b25453c23b7c04cfdaccc01",
"structkaldi_1_1TxpLtsTree.html#a18eb67f2a9e7806f7473a2b5f97a53d9",
"structkaldi_1_1nnet1_1_1Component.html#a81f78fc173dedefe5a049c0aa3eed2c0ac71af5a6c46da4fd968deaca5f086a7d",
"structkaldi_1_1nnet3_1_1BatchNormComponent_1_1Memo.html#a610dc0905fcc6ea9368ef1fdd22fce11",
"structkaldi_1_1nnet3_1_1NetworkNode.html#a5acc26da16e3a27d76b93e018d1a6d4f",
"structkaldi_1_1nnet3_1_1NnetSimpleComputationOptions.html#adf28936259c04ff2a4c4d1af293ffea9",
"table-types_8h.html#gaed9a47f36b8c2d32caaa8f13ca19f192",
"txplts_8h.html#a1827094d9bd50b94fa8c17930925f412"
];

var SYNCONMSG = 'click to disable panel synchronisation';
var SYNCOFFMSG = 'click to enable panel synchronisation';