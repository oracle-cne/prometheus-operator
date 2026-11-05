# metrics-gen

`metrics-gen` is a code generator for Kubernetes operators. It scans Go API packages for types annotated with `+metrics:conditions:` markers and generates a [Prometheus](https://prometheus.io/) collector that exposes a `status_condition` gauge metric for each annotated resource type.

## Usage

### 1. Annotate your API type

Add a `+metrics:conditions:` marker comment immediately before the struct declaration:

```go
// +metrics:conditions:path=.status.conditions,resourceType=my_resource
type MyResource struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   MyResourceSpec   `json:"spec,omitempty"`
    Status MyResourceStatus `json:"status,omitempty"`
}
```

The marker fields are:

| Field          | Description                                              |
|----------------|----------------------------------------------------------|
| `path`         | Dot-separated path to the conditions slice on the struct |
| `resourceType` | Resource name used in the metric name and output path    |

### 2. Run the generator

```sh
metrics-gen \
  --api-dir        ./pkg/apis \
  --module         github.com/myorg/myoperator \
  --out-dir        ./pkg/metrics \
  --metric-namespace my_operator \
  --go-header-file  ./hack/boilerplate.go.txt
```

This writes `./pkg/metrics/my_resource/metrics.go` containing a `NewConditionCollector` constructor.

The generated metric has the form:

```
<namespace>_<resourceType>_status_condition{condition="xxx",status="xxx"} 0|1
```

### 3. Register the collector

The registration happens typically during the initialization of the controller. Here is an example based on the [controller-runtime](https://github.com/kubernetes-sigs/controller-runtime) library.

```go
import (
    "iter"

    "github.com/prometheus/client_golang/prometheus"
    "sigs.k8s.io/controller-runtime/pkg/metrics"

    prommetrics "github.com/myorg/myoperator/pkg/metrics/prometheus"
    "github.com/myorg/myoperator/pkg/apis/my_resource/v1"
)

func RegisterWithManager(mgr ctrl.Manager, opts Options) error {
    // Initiliaze the informers and all other stuff.

    // Build an iterator that returns all the resources from the controller's cache.
    myResourceSeq := func(yield func(*v1.MyResource) bool) {
        // Get the resources from the client and call yield() for each.
    }
    if err: = metrics.Registry.Register(prommetrics.NewConditionCollector(myResourceSeq)); err != nil {
        return err
    }
}
```

`NewConditionCollector` accepts an `iter.Seq[*v1.MyResource]` — any iterator over pointers to your resource type.


## Flags

| Flag                 | Default          | Description                                     |
|----------------------|------------------|-------------------------------------------------|
| `--api-dir`          | _(required)_     | Root of the API module to scan                  |
| `--module`           | _(required)_     | Root Go module path of the output project       |
| `--out-dir`          | `./pkg/metrics`  | Directory where generated packages are written  |
| `--metric-namespace` | _(empty)_        | First component of the Prometheus metric name   |
| `--go-header-file`   | _(empty)_        | File whose contents are prepended to each output file |

## License

Apache License 2.0 — see [LICENSE](LICENSE).
