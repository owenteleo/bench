{ pkgs ? import <nixpkgs> {
    overlays = [ (import ./nix/arm-toolchain.nix) ];
  }
}:
  pkgs.mkShell {
    nativeBuildInputs = with pkgs.buildPackages; [
      arm-toolchain
      ncurses5
      openocd
      python3
    ];

  shellHook = ''
    export LD_LIBRARY_PATH=/nix/store/jwfdb6ygf4zniyhw7xy6pnvgf495ajqq-ncurses-abi5-compat-6.4.20221231/lib:$LD_LIBRARY_PATH

    if [ ! -d venv ]; then
      python3 -m venv venv
    fi
    source venv/bin/activate
  '';

}

