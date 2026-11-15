import io
from kaitaistruct import KaitaiStream
from operator import attrgetter


def process_Frames(kaitai_interface, data):
    index = 0
    frames = []
    while index < len(data):
        current_stream = KaitaiStream(io.BytesIO(data[index:]))
        # Note that this has been tested to work with version 0.11
        try:
            frame = kaitai_interface(current_stream)
            bytes_processed = current_stream.pos()

            if bytes_processed == 0:
                index += 1
            else:
                index += bytes_processed
                frames.append(frame)
        except Exception as e:
            index += 1
    return frames


def extract_paths(record):
    fields = record.__doc__.split("\n")
    paths = []
    for field in fields:
        if field.find(":") == -1:
            continue
        field = field.split(":")[-1].strip()
        paths.append(field)
    return paths


def create_kaitai_dictionary(record):
    paths = extract_paths(record)
    record_dict = dict()
    for path in paths:
        try:
            record_dict[path] = attrgetter(path)(record)
        except:
            pass
    return record_dict
