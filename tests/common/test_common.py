from unittest.mock import Mock, patch

from app.common.utils import load_private_key


def test_load_private_key():
    # Mock the load_pem_private_key method
    mock_key = Mock()
    with patch(
        "cryptography.hazmat.primitives.serialization.load_pem_private_key",
        return_value=mock_key,
    ):
        # Call the function that uses load_pem_private_key
        key = load_private_key(b"private_key", "passphrase")

        # Assertions
        assert key == mock_key.private_bytes.return_value

