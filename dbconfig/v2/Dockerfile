FROM postgres:13

# Install required packages for building the extension
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-server-dev-13 \
    build-essential \
    git

# Clone the pgvector repository and build the extension
RUN git clone https://github.com/ottogroup/pgvector.git && \
    cd pgvector && \
    make && \
    make install

# Add pgvector to shared_preload_libraries in the postgresql.conf file
RUN echo "shared_preload_libraries = 'pgvector'" >> /usr/share/postgresql/postgresql.conf.sample
