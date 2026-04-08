const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const fs = require('fs');

// 因为项目没有现成的 .proto 文件供客户端使用（使用了通用 Struct），
// 我们可以通过声明一个临时的 .proto 来加载 gRPC 服务定义。
const PROTO_CONTENT = `
syntax = "proto3";
package apipy.heartbeat.v1;
import "google/protobuf/struct.proto";

service HeartbeatService {
  rpc ReportHeartbeat(google.protobuf.Struct) returns (google.protobuf.Struct);
}
`;

fs.writeFileSync('temp.proto', PROTO_CONTENT);

// 动态加载 proto 文件
const packageDefinition = protoLoader.loadSync('temp.proto', {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
const heartbeat = protoDescriptor.apipy.heartbeat.v1;

// TODO: 这里填入你的云端 Linux 服务器 IP 和端口，默认是 50051
const SERVER_ADDRESS = '127.0.0.1:50051'; 

// 创建非加密（Insecure）的连接通道
const client = new heartbeat.HeartbeatService(SERVER_ADDRESS, grpc.credentials.createInsecure());

// 构造请求体：由于请求参数是 google.protobuf.Struct，因此结构需要按照 fields 和 Value 来填充
const req = {
  fields: {
    device_name: { stringValue: 'Mac_Test_01' },
    timestamp: { numberValue: Date.now() / 1000 } // 秒级时间戳
  }
};

console.log(`正在连接 gRPC 服务: ${SERVER_ADDRESS} ...`);

client.ReportHeartbeat(req, (err, response) => {
  if (err) {
    console.error('❌ 请求失败:', err.message);
  } else {
    console.log('✅ 请求成功, 响应结果:');
    console.log(JSON.stringify(response, null, 2));
  }
  
  // 清理临时生成的 proto 文件
  try { fs.unlinkSync('temp.proto'); } catch(e) {}
});
