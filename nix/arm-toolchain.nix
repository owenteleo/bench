# This is a hard-coded overlay for a particular version of the binary ARM embedded toolchain.
# When the toolchain used by the Teleo embedded team is updated this will need to be as well.

self: super: {
  arm-toolchain = super.stdenv.mkDerivation rec {
    pname = "gcc-arm-none-eabi";
    version = "9-2019-q4-major";
    src = super.fetchurl {
      url = "https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/gcc-arm-none-eabi-9-2019-q4-major-x86_64-linux.tar.bz2?revision=108bd959-44bd-4619-9c19-26187abf5225&rev=108bd95944bd46199c1926187abf5225&hash=3587BB8F9E458752D7057C56DCF3171DEC0463B4";
      sha256 = "vNhA+DnVv0knljjp9niQsu86fJx6myUnHoPsT/QdF3o=";
    };
    unpackPhase = ''
      mkdir -p $out
      tar -xjf ${src} --directory=$out
    '';
    installPhase = ''
      # Move everything from the extracted folder to the output directory
      mv $out/gcc-arm-none-eabi-${version}/* $out/
      rmdir $out/gcc-arm-none-eabi-${version}
    '';
    meta = with super.stdenv.lib; {
      description = "ARM GCC toolchain for embedded development (arm-none-eabi)";
      maintainers = [ "owenteleo" ];
    };
  };
}

