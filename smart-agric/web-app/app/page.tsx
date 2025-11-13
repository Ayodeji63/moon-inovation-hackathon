"use client";
import React, { useState } from "react";
import * as Accordion from "@radix-ui/react-accordion";
import {
  ChevronDown,
  Droplets,
  Wifi,
  TrendingUp,
  MapPin,
  BarChart3,
  Zap,
} from "lucide-react";

export default function AgriPalLanding() {
  const [email, setEmail] = useState("");

  const features = [
    {
      icon: <Droplets className="w-8 h-8" />,
      title: "Real-time Soil Monitoring",
      description:
        "Get live data on moisture levels, nutrients, and pH directly from your fields.",
    },
    {
      icon: <Wifi className="w-8 h-8" />,
      title: "Intelligent Irrigation",
      description:
        "Receive watering schedules optimized for your crops and forecasts to save water.",
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "NASA-Powered Insights",
      description:
        "Leverage satellite data and AI-driven analytics to optimize your productivity.",
    },
  ];

  const steps = [
    {
      number: "1",
      title: "Place Sensors",
      description: "Easily install our plug-and-play sensors across your farm.",
    },
    {
      number: "2",
      title: "Get Real-time Data",
      description:
        "Data flows directly to your AgriPal dashboard in any device.",
    },
    {
      number: "3",
      title: "Irrigate Intelligently",
      description:
        "Receive actionable recommendations and automate your irrigation systems.",
    },
  ];

  const farmData = [
    {
      icon: <MapPin className="w-5 h-5" />,
      label: "Farm A",
      value: "Soil Moisture Creator: Irrigating soon.",
    },
    {
      icon: <BarChart3 className="w-5 h-5" />,
      label: "Farm B",
      value: "Nitrogen levels are optimal. Great job!",
    },
    {
      icon: <Zap className="w-5 h-5" />,
      label: "Farm C",
      value: "Need to re-calibrate soil ion tomorrow; find a soil manager.",
    },
  ];

  const faqs = [
    {
      question: "How difficult is it to set up the sensors?",
      answer:
        "Setting up AgriPal sensors is incredibly easy! Our plug-and-play system requires no technical expertise. Simply place the sensors in your fields, connect them to the app, and you're ready to start receiving data within minutes.",
    },
    {
      question: "What is the pricing model?",
      answer:
        "We offer flexible pricing plans based on farm size and number of sensors. Our basic plan starts at an affordable monthly rate, with enterprise options available for larger operations. Contact our sales team for a custom quote.",
    },
    {
      question: "Is my data secure?",
      answer:
        "Absolutely. We use bank-level encryption to protect your farm data. All information is stored securely in the cloud with regular backups, and we never share your data with third parties without your explicit consent.",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2L2 7v10c0 5.5 3.8 10.7 10 12 6.2-1.3 10-6.5 10-12V7l-10-5zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-gray-900">AgriPal</h1>
            </div>

            <nav className="hidden md:flex items-center gap-8">
              <a
                href="#features"
                className="text-sm text-gray-600 hover:text-gray-900 transition"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                className="text-sm text-gray-600 hover:text-gray-900 transition"
              >
                How It Works
              </a>
              <a
                href="#faq"
                className="text-sm text-gray-600 hover:text-gray-900 transition"
              >
                FAQ
              </a>
              <button className="bg-green-500 text-white text-sm font-semibold px-6 py-2 rounded-full hover:bg-green-600 transition">
                Sign Up
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div
            className="relative h-[500px] rounded-3xl overflow-hidden bg-cover bg-center"
            style={{
              backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.4)), url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80')`,
            }}
          >
            <div className="absolute inset-0 flex flex-col justify-end p-12">
              <h2 className="text-5xl font-bold text-white mb-4 max-w-2xl">
                Your Soil Talks. AgriPal Listens.
              </h2>
              <p className="text-white/90 text-lg mb-8 max-w-xl">
                Smart sensors and AI-driven insights to supercharge your
                agricultural yields, reduce water waste.
              </p>
              <div className="flex gap-4">
                <button className="bg-green-500 text-white font-semibold px-8 py-3 rounded-full hover:bg-green-600 transition">
                  Join Beta
                </button>
                <button className="bg-white text-gray-900 font-semibold px-8 py-3 rounded-full hover:bg-gray-100 transition">
                  Learn More
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Farm Data Section */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <h3 className="text-center text-2xl font-bold text-gray-900 mb-12">
            Listen to What Your Farm is Telling You
          </h3>

          <div className="space-y-6 max-w-2xl mx-auto">
            {farmData.map((item, index) => (
              <div
                key={index}
                className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl"
              >
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-green-600 flex-shrink-0">
                  {item.icon}
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 mb-1">
                    {item.label}
                  </div>
                  <div className="text-gray-600 text-sm">{item.value}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Stop Guessing. Start Growing
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              AgriPal lifts the guesswork out of farming with precise, real-time
              data. Water less, produce more.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center text-green-600 mx-auto mb-6">
                  {feature.icon}
                </div>
                <h4 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h4>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Simple Steps to a Smarter Farm
            </h3>
            <p className="text-gray-600">
              Getting started with AgriPal is as easy as 1, 2, 3.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-green-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                  {step.number}
                </div>
                <h4 className="text-xl font-bold text-gray-900 mb-3">
                  {step.title}
                </h4>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-6">
          <div className="bg-gray-900 rounded-3xl p-8 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h4 className="text-white text-xl font-bold mb-1">
                  Browse AgriPal
                </h4>
                <p className="text-gray-400 text-sm">My Embedded Tab</p>
              </div>
              <div className="flex gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-2">
                  Internal Measurement
                </div>
                <div className="h-32 bg-gradient-to-r from-green-500/20 to-green-600/20 rounded-lg relative overflow-hidden">
                  <svg
                    className="w-full h-full"
                    viewBox="0 0 300 100"
                    preserveAspectRatio="none"
                  >
                    <path
                      d="M0,50 Q50,20 100,40 T200,50 T300,30"
                      stroke="#22c55e"
                      strokeWidth="2"
                      fill="none"
                    />
                  </svg>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="w-16 h-16 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <div className="text-white font-semibold mb-1">
                      Optimal Zone
                    </div>
                    <div className="text-gray-400 text-sm">
                      Your soil is in the ideal range
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-16 bg-white">
        <div className="max-w-3xl mx-auto px-6">
          <h3 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Frequently Asked Questions
          </h3>

          <Accordion.Root type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <Accordion.Item
                key={index}
                value={`item-${index}`}
                className="border border-gray-200 rounded-xl overflow-hidden"
              >
                <Accordion.Header>
                  <Accordion.Trigger className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition group">
                    <span className="font-semibold text-gray-900">
                      {faq.question}
                    </span>
                    <ChevronDown className="w-5 h-5 text-gray-500 transition-transform group-data-[state=open]:rotate-180" />
                  </Accordion.Trigger>
                </Accordion.Header>
                <Accordion.Content className="px-6 pb-6 text-gray-600 leading-relaxed">
                  {faq.answer}
                </Accordion.Content>
              </Accordion.Item>
            ))}
          </Accordion.Root>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-br from-green-50 to-green-100">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h3 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Transform Your Farm?
          </h3>
          <p className="text-gray-600 mb-8">
            Join the future of farming today. AgriPal makes data-driven farming
            accessible, simple, and cost easily. Learn more, or book a demo.
          </p>

          <div className="flex gap-4 justify-center items-center max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 px-6 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button className="bg-green-500 text-white font-semibold px-8 py-3 rounded-full hover:bg-green-600 transition whitespace-nowrap">
              Get Beta
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="text-white font-bold mb-4">AgriPal</h4>
              <p className="text-sm">
                Making farming more intelligent and sustainable.
              </p>
            </div>

            <div>
              <h5 className="text-white font-semibold mb-4">Product</h5>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="#" className="hover:text-white transition">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">
                    How It Works
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">
                    Pricing
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h5 className="text-white font-semibold mb-4">Company</h5>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="#" className="hover:text-white transition">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">
                    Careers
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h5 className="text-white font-semibold mb-4">Legal</h5>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="#" className="hover:text-white transition">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">
                    Terms of Service
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex justify-between items-center">
            <p className="text-sm">© 2024 AgriPal. All rights reserved.</p>
            <div className="flex gap-4">
              <a href="#" className="hover:text-white transition">
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
                </svg>
              </a>
              <a href="#" className="hover:text-white transition">
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
