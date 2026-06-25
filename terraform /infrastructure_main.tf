# infrastructure/main.tf
resource "aws_kinesis_stream" "txn_stream" {
  name        = "transaction-stream"
  shard_count = 2
}

resource "aws_s3_bucket" "txn_bucket" {
  bucket = "transaction-monitoring-data"
}
