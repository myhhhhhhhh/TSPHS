GNN_HOME=../../graphnn-bdf51e6

include $(GNN_HOME)/make_common

lib_dir = $(GNN_HOME)/build_cpuonly/lib
gnn_lib = $(lib_dir)/libgnn.a

include_dirs = $(CUDA_HOME)/include $(MKL_ROOT)/include $(GNN_HOME)/include ./include

CXXFLAGS += $(addprefix -I,$(include_dirs)) -Wno-unused-local-typedef
CXXFLAGS += -fPIC
# CXXFLAGS += -fPIC -DUSE_GPU
# CXXFLAGS += -DGPU_MODE
cpp_files = $(shell $(FIND) src/lib -name "*.cpp" -printf "%P\n")
cxx_obj_files = $(subst .cpp,.o,$(cpp_files))

objs = $(addprefix build/lib/,$(cxx_obj_files))
DEPS = $(objs:.o=.d)

target = build/dll/libtsp2d.so
target_dep = $(addsuffix .d,$(target))

.PRECIOUS: build/lib/%.o

all: $(target)

build/dll/libtsp2d.so : src/tsp2d_lib.cpp $(gnn_lib) $(objs)
	$(dir_guard)
	$(CXX) -shared $(CXXFLAGS) -MMD -o $@ $(filter %.cpp %.o, $^) -L$(lib_dir) -lgnn $(LDFLAGS)

DEPS += $(target_dep)

build/lib/%.o: src/lib/%.cpp
	$(dir_guard)
	$(CXX) $(CXXFLAGS) -MMD -c -o $@ $(filter %.cpp, $^)

clean:
	rm -rf build

-include $(DEPS)
