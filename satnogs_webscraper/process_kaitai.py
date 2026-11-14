import io
from kaitaistruct import KaitaiStream


def process_Frames(kaitai_interface, data):
    index = 0
    frames = []
    while index < len(data):
        current_stream = KaitaiStream(io.BytesIO(data[index:]))
        # Note that this has been tested to work with version 0.11
        try:
            frame = kaitai_interface(current_stream)
            bytes_processed = current_stream.pos

            if bytes_processed == 0:
                index += 1
            else:
                index += bytes_processed
                frames.append(frame)
        except Exception as e:
            index += 1
    return frames
