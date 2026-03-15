import logging
import os
from concurrent import futures

import django
import grpc
from google.protobuf import struct_pb2


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')
django.setup()

from zapp.services.heartbeat_service import report_heartbeat


logger = logging.getLogger("grpc.heartbeat")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def _extract_peer_ip(peer):
    if not peer:
        return ''
    if peer.startswith('ipv4:') or peer.startswith('ipv6:'):
        raw = peer.split(':', 1)[1]
        if raw.startswith('['):
            end = raw.find(']')
            if end > 0:
                return raw[1:end]
            return raw
        if ':' in raw:
            return raw.rsplit(':', 1)[0]
        return raw
    return peer


def _get_struct_value(message, key):
    field = message.fields.get(key)
    if not field:
        return None
    if field.HasField('string_value'):
        return field.string_value
    if field.HasField('number_value'):
        return field.number_value
    if field.HasField('bool_value'):
        return field.bool_value
    return None


def _make_response_struct(code, message, data=None):
    response = struct_pb2.Struct()
    response['code'] = float(code)
    response['message'] = message
    if data:
        data_struct = struct_pb2.Struct()
        for k, v in data.items():
            data_struct[k] = v
        response['data'] = data_struct
    return response


def report_heartbeat_grpc(request, context):
    try:
        device_name = _get_struct_value(request, 'device_name')
        timestamp = _get_struct_value(request, 'timestamp')
        peer_ip = _extract_peer_ip(context.peer())
        result = report_heartbeat(
            device_name=device_name,
            timestamp=timestamp,
            ip_address=peer_ip,
        )
        return _make_response_struct(200, "Heartbeat received", result)
    except ValueError as e:
        return _make_response_struct(400, str(e))
    except Exception as e:
        logger.exception("grpc heartbeat failed")
        return _make_response_struct(500, str(e))


def create_server():
    service_name = "apipy.heartbeat.v1.HeartbeatService"
    method_handlers = {
        "ReportHeartbeat": grpc.unary_unary_rpc_method_handler(
            report_heartbeat_grpc,
            request_deserializer=struct_pb2.Struct.FromString,
            response_serializer=struct_pb2.Struct.SerializeToString,
        )
    }
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_generic_rpc_handlers((
        grpc.method_handlers_generic_handler(service_name, method_handlers),
    ))
    return server


def main():
    port = int(os.environ.get('GRPC_HEARTBEAT_PORT', '50051'))
    server = create_server()
    bind_addr = f'[::]:{port}'
    server.add_insecure_port(bind_addr)
    server.start()
    logger.info(f"gRPC Heartbeat server started on {bind_addr}")
    server.wait_for_termination()


if __name__ == '__main__':
    main()
