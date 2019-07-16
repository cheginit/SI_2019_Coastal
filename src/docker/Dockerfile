FROM continuumio/miniconda3

RUN conda install -c conda-forge xarray cartopy pynio pseudonetcdf \
    pandas matplotlib ffmpeg imagemagick tqdm

RUN useradd -ms /bin/bash plot
USER plot
WORKDIR /home/plot
RUN ["chown", "-R", "plot", "/home/plot"]
VOLUME ["/home/plot"]

CMD ["/bin/bash"]
