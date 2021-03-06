Using Caffe (http://caffe.berkeleyvision.org/), cnn_feature_extractor extracts a feature vector from each input image. It is assumed Caffe has been built with CMake, and the header files and library (libcaffe.so) are available through CMake-generated CaffeConfig.cmake.

To run the program, first download two files from Caffe and copy them to
${SMQTK_BINARY_DIR}/data/caffenet.
1) bvlc_reference_caffenet.caffemodel
   run `scripts/download_model_binary.py models/bvlc_reference_caffenet` from Caffe root directory
2) imagenet_mean.binaryproto
   wget http://dl.caffe.berkeleyvision.org/caffe_ilsvrc12.tar.gz

Then customize imagenet_val.prototxt. Make sure layer.transform_param.mean_file points to imagenet_mean.binaryprot, and layer.image_data_param.soruce points to file_list.txt. Change layer.image_data_param.batch_size to 50 (or 1) and the second to last parameter on the following command line to 10 (or 3).

Finally run the following command from the shell
cd ${SMQTK_BINARY_DIR}

./src/cnn_feature_extractor/cnn_feature_extractor data/caffenet/bvlc_reference_caffenet.caffemodel data/caffenet/imagenet_val.prototxt fc7 data/caffenet/cnn 3 csv

./src/cnn_feature_extractor/cnn_feature_extractor data/caffenet/bvlc_reference_caffenet.caffemodel data/caffenet/imagenet_val.prototxt fc7 data/caffenet/cnn 3 svm

./src/cnn_feature_extractor/cnn_feature_extractor data/caffenet/bvlc_reference_caffenet.caffemodel data/caffenet/imagenet_val.prototxt fc7 data/caffenet/cnn 3 stdout >& /dev/null

If you get a segfault, double check the settings in imagenet_val.prototxt.
