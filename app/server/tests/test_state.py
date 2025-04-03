import asyncio
from unittest import mock

import pytest
from fastapi import FastAPI
from playwright.async_api import Browser

from server import state
from server.state import lifespan


@pytest.fixture
def mock_settings():
    with mock.patch('server.state.settings') as mock_settings:
        mock_settings.VERSION = 'test_version'
        mock_settings.BASIC_HTPASSWD = None
        mock_settings.BROWSER_TYPE = mock.Mock(value='chromium')
        mock_settings.BROWSER_CONTEXT_LIMIT = 20
        yield mock_settings


@pytest.mark.asyncio
async def test_lifespan_no_credentials(mock_settings):
    app = FastAPI()
    async with lifespan(app) as state_instance:
        assert state_instance['basic_auth_credentials'] is None
        assert isinstance(state_instance['browser'], Browser)
        assert isinstance(state_instance['semaphore'], asyncio.Semaphore)


@pytest.mark.asyncio
async def test_lifespan_with_credentials_file_not_found(mock_settings, tmp_path):
    mock_settings.BASIC_HTPASSWD = str(tmp_path / 'non_existent.htpasswd')

    app = FastAPI()
    async with lifespan(app) as state_instance:
        assert state_instance['basic_auth_credentials'] is None
        assert isinstance(state_instance['browser'], Browser)
        assert isinstance(state_instance['semaphore'], asyncio.Semaphore)


@pytest.mark.asyncio
async def test_lifespan_with_credentials_file(mock_settings, tmp_path):
    htpasswd_file = tmp_path / 'test.htpasswd'
    htpasswd_content = 'user1:hash1\nuser2:hash2'
    htpasswd_file.write_text(htpasswd_content)
    mock_settings.BASIC_HTPASSWD = str(htpasswd_file)

    app = FastAPI()
    async with lifespan(app) as state_instance:
        assert state_instance['basic_auth_credentials'] == {'user1': 'hash1', 'user2': 'hash2'}
        assert isinstance(state_instance['browser'], Browser)
        assert isinstance(state_instance['semaphore'], asyncio.Semaphore)


def test_state_typed_dict():
    # Test that State is a properly defined TypedDict
    state_dict = state.State(basic_auth_credentials={'user': 'hash'}, browser=mock.Mock(), semaphore=asyncio.Semaphore(1))
    assert state_dict['basic_auth_credentials'] == {'user': 'hash'}
