resource "aws_route53_record" "app-bluezoneautomation-com-CNAME" {
  zone_id = data.aws_route53_zone.default.zone_id
  name    = "app.bluezoneautomation.com."
  type    = "CNAME"
  ttl     = 60
  records = [aws_lb.default.dns_name]
}
