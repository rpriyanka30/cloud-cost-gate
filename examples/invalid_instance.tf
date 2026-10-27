provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "test_server" {
  ami           = "ami-12345678"
  instance_type = "t3.unknown"
}