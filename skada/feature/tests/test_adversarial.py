# Author: Theo Gnassounou <theo.gnassounou@inria.fr>
#         Remi Flamary <remi.flamary@polytechnique.edu>
#
# License: BSD 3-Clause

import pytest
import torch
from torch import nn

from skada.feature import CDAN, DANN
from skada.feature._modules import DomainClassifier, ToyCNN


@pytest.mark.parametrize(
    "input_size, n_channels, n_classes",
    [(100, 2, 5), (120, 1, 3)],
)
def test_dann(input_size, n_channels, n_classes):
    module = ToyCNN(
        n_channels=n_channels, input_size=input_size, n_classes=n_classes, kernel_size=8
    )
    module.eval()

    rng = torch.random.manual_seed(42)
    n_samples = 20
    X = torch.randn(size=(n_samples, n_channels, input_size), generator=rng)
    y = torch.randint(high=n_classes, size=(n_samples,), generator=rng)
    X_target = torch.randn(size=(n_samples, n_channels, input_size), generator=rng)

    method = DANN(
        module=module,
        criterion=nn.CrossEntropyLoss(),
        layer_names=["feature_extractor"],
        max_epochs=2,
        domain_classifier=DomainClassifier,
        domain_classifier__len_last_layer=module.len_last_layer,
        domain_criterion=nn.BCELoss,
    )
    method.fit(X, y, X_target=X_target)
    y_pred = method.predict(X_target)

    assert y_pred.shape[0] == n_samples


@pytest.mark.parametrize(
    "input_size, n_channels, n_classes, max_features",
    [(100, 2, 5, 100), (120, 1, 3, 4096)],
)
def test_cdan(input_size, n_channels, n_classes, max_features):
    module = ToyCNN(
        n_channels=n_channels, input_size=input_size, n_classes=n_classes, kernel_size=8
    )
    module.eval()

    rng = torch.random.manual_seed(42)
    n_samples = 20
    X = torch.randn(size=(n_samples, n_channels, input_size), generator=rng)
    y = torch.randint(high=n_classes, size=(n_samples,), generator=rng)
    X_target = torch.randn(size=(n_samples, n_channels, input_size), generator=rng)
    input_size_domain_classifier = module.len_last_layer * n_classes
    if input_size_domain_classifier > max_features:
        input_size_domain_classifier = max_features

    method = CDAN(
        module=module,
        criterion=nn.CrossEntropyLoss(),
        layer_names=["feature_extractor"],
        max_epochs=2,
        domain_classifier=DomainClassifier,
        domain_classifier__len_last_layer=input_size_domain_classifier,
        domain_criterion=nn.BCELoss,
        max_features=max_features,
    )
    method.fit(X, y, X_target=X_target)
    y_pred = method.predict(X_target)

    assert y_pred.shape[0] == n_samples
