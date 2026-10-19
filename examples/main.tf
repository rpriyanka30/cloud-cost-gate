provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web_server" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }
}

resource "aws_db_instance" "app_database" {
  identifier        = "cloud-cost-gate-db"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  engine            = "mysql"
}