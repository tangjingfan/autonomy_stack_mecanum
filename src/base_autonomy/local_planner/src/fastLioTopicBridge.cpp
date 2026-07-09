#include <memory>
#include <string>

#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>

class FastLioTopicBridge : public rclcpp::Node
{
public:
  FastLioTopicBridge()
  : Node("fastLioTopicBridge")
  {
    const std::string input_odom_topic =
      declare_parameter<std::string>("input_odom_topic", "/Odometry");
    const std::string input_cloud_topic =
      declare_parameter<std::string>("input_cloud_topic", "/cloud_registered");
    const std::string output_odom_topic =
      declare_parameter<std::string>("output_odom_topic", "/state_estimation");
    const std::string output_cloud_topic =
      declare_parameter<std::string>("output_cloud_topic", "/registered_scan");

    const auto output_qos = rclcpp::QoS(rclcpp::KeepLast(10)).reliable();
    const auto input_qos = rclcpp::SensorDataQoS();

    if (input_odom_topic != output_odom_topic) {
      odom_pub_ = create_publisher<nav_msgs::msg::Odometry>(output_odom_topic, output_qos);
      odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
        input_odom_topic, input_qos,
        [this](const nav_msgs::msg::Odometry::SharedPtr msg) {
          odom_pub_->publish(*msg);
        });
      RCLCPP_INFO(
        get_logger(), "Relaying odometry: %s -> %s",
        input_odom_topic.c_str(), output_odom_topic.c_str());
    } else {
      RCLCPP_INFO(get_logger(), "Odometry input already uses %s", output_odom_topic.c_str());
    }

    if (input_cloud_topic != output_cloud_topic) {
      cloud_pub_ = create_publisher<sensor_msgs::msg::PointCloud2>(output_cloud_topic, output_qos);
      cloud_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
        input_cloud_topic, input_qos,
        [this](const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
          cloud_pub_->publish(*msg);
        });
      RCLCPP_INFO(
        get_logger(), "Relaying cloud: %s -> %s",
        input_cloud_topic.c_str(), output_cloud_topic.c_str());
    } else {
      RCLCPP_INFO(get_logger(), "Cloud input already uses %s", output_cloud_topic.c_str());
    }
  }

private:
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_sub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_pub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FastLioTopicBridge>());
  rclcpp::shutdown();
  return 0;
}
