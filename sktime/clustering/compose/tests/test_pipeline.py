# copyright: sktime developers, BSD-3-Clause License (see LICENSE file)
"""Unit tests for (dunder) composition functionality attached to the base class."""

__author__ = ["fkiraly"]
__all__ = []

import pytest
from sklearn.preprocessing import StandardScaler

from sktime.clustering.compose import ClustererPipeline
from sktime.clustering.k_means import TimeSeriesKMeans
from sktime.clustering.kernel_k_means import TimeSeriesKernelKMeans
from sktime.transformations.panel.padder import PaddingTransformer
from sktime.transformations.series.exponent import ExponentTransformer
from sktime.transformations.series.impute import Imputer
from sktime.utils._testing.estimator_checks import _assert_array_almost_equal
from sktime.utils._testing.panel import _make_panel_X
from sktime.utils.validation._dependencies import _check_estimator_deps


@pytest.mark.skipif(
    not _check_estimator_deps(TimeSeriesKernelKMeans, severity="none"),
    reason="skip test if required soft dependencies not available",
)
def test_dunder_mul():
    """Test the mul dunder method."""
    RAND_SEED = 42
    X = _make_panel_X(n_instances=10, n_timepoints=20, random_state=RAND_SEED)
    X_test = _make_panel_X(n_instances=5, n_timepoints=20, random_state=RAND_SEED)

    t1 = ExponentTransformer(power=4)
    t2 = ExponentTransformer(power=0.25)

    c = TimeSeriesKernelKMeans(random_state=RAND_SEED)
    t12c_1 = t1 * (t2 * c)
    t12c_2 = (t1 * t2) * c
    t12c_3 = t1 * t2 * c

    assert isinstance(t12c_1, ClustererPipeline)
    assert isinstance(t12c_2, ClustererPipeline)
    assert isinstance(t12c_3, ClustererPipeline)

    y_pred = c.fit(X).predict(X_test)

    _assert_array_almost_equal(y_pred, t12c_1.fit(X).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_2.fit(X).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_3.fit(X).predict(X_test))


@pytest.mark.skipif(
    not _check_estimator_deps(TimeSeriesKMeans, severity="none"),
    reason="skip test if required soft dependencies not available",
)
def test_mul_sklearn_autoadapt():
    """Test auto-adapter for sklearn in mul."""
    RAND_SEED = 42
    X = _make_panel_X(n_instances=10, n_timepoints=20, random_state=RAND_SEED)
    X_test = _make_panel_X(n_instances=10, n_timepoints=20, random_state=RAND_SEED)

    t1 = ExponentTransformer(power=2)
    t2 = StandardScaler()
    c = TimeSeriesKMeans(random_state=RAND_SEED)

    t12c_1 = t1 * (t2 * c)
    t12c_2 = (t1 * t2) * c
    t12c_3 = t1 * t2 * c

    assert isinstance(t12c_1, ClustererPipeline)
    assert isinstance(t12c_2, ClustererPipeline)
    assert isinstance(t12c_3, ClustererPipeline)

    y_pred = t12c_1.fit(X).predict(X_test)

    _assert_array_almost_equal(y_pred, t12c_2.fit(X).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_3.fit(X).predict(X_test))


@pytest.mark.skipif(
    not _check_estimator_deps(TimeSeriesKMeans, severity="none"),
    reason="skip test if required soft dependencies not available",
)
def test_missing_unequal_tag_inference():
    """Test that ClustererPipeline infers missing/unequal tags correctly."""
    c = TimeSeriesKMeans()
    c1 = ExponentTransformer() * PaddingTransformer() * ExponentTransformer() * c
    c2 = ExponentTransformer() * ExponentTransformer() * c
    c3 = Imputer() * ExponentTransformer() * c
    c4 = ExponentTransformer() * Imputer() * c

    assert c1.get_tag("capability:unequal_length")
    assert not c2.get_tag("capability:unequal_length")
    assert c3.get_tag("capability:missing_values")
    assert not c4.get_tag("capability:missing_values")
