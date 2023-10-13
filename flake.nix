{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  outputs = {nixpkgs, ...}: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = [ 
				pkgs.python311
				pkgs.poetry
			];
		  POETRY_VIRTUALENVS_IN_PROJECT = "true";
		  POETRY_VIRTUALENVS_PATH = "{project-dir}/.venv";
		  POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON = "true";
    };
  };
}
