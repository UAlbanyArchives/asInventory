import os
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class RuntimePaths:
    base_dir: str
    input_path: str
    output_path: str
    complete_path: str
    dao_path: str
    error_log_path: str


def is_frozen_app() -> bool:
    return getattr(sys, 'frozen', False)


def default_base_dir() -> str:
    env_base_dir = os.environ.get('ASINVENTORY_BASE_DIR')
    if env_base_dir:
        return env_base_dir
    if is_frozen_app():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_repository_id(default: str = '2') -> str:
    return '2'


def build_runtime_paths(
    base_dir: Optional[str] = None,
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    complete_path: Optional[str] = None,
    dao_path: Optional[str] = None,
) -> RuntimePaths:
    resolved_base_dir = os.path.abspath(base_dir or default_base_dir())
    paths = RuntimePaths(
        base_dir=resolved_base_dir,
        input_path=os.path.abspath(input_path) if input_path else os.path.join(resolved_base_dir, 'input'),
        output_path=os.path.abspath(output_path) if output_path else os.path.join(resolved_base_dir, 'output'),
        complete_path=os.path.abspath(complete_path) if complete_path else os.path.join(resolved_base_dir, 'complete'),
        dao_path=os.path.abspath(dao_path) if dao_path else os.path.join(resolved_base_dir, 'dao'),
        error_log_path=os.path.join(resolved_base_dir, 'error.log'),
    )
    return paths


def ensure_runtime_directories(paths: RuntimePaths) -> None:
    for directory in (paths.input_path, paths.output_path, paths.complete_path, paths.dao_path):
        if not os.path.isdir(directory):
            os.mkdir(directory)
