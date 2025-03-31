# Intro to Controls Workshop

Welcome! 👋  
This repo is a beginner-friendly controls workshop designed to teach the fundamentals of PID control through simulation and hands-on experimentation. You'll get to tweak a PID controller and see how it behaves when controlling a physical system — all in Python, with live visual feedback.

## 🔍 What This Is

This workshop simulates a simple physical system (like a mass-damper or spring-mass-damper model) and gives you a chance to write and tune a PID controller to track a desired position. You’ll see:

- How P, I, and D each affect system behavior
- Why some systems require integral action to remove steady-state error
- How saturation, noise, and modeling choices affect your control

Great for:
- Newbies learning about control theory
- Engineering students looking for intuition
- Anyone who likes tweaking gains until stuff stops oscillating

---

## 🛠️ Setup Instructions

Clone the repository and install the required dependencies.

### 1. Clone the Repo

```
bash
git clone https://github.com/sahil-kale/intro-to-controls-workshop.git
cd intro-to-controls-workshop
```

### 2. Install requirements
`pip install -r scripts/python_requirements.txt`

## 🚀 Running the Workshop
Write the PID controller in `controller_implemented.py`

Then, run `python3 simulator/simulator.py`

## Some notes

### Window size
If you find that the pygame window does not fit, change the width and height accordingly in `simulator.py` on line 100.

### It's actually gain-scheduled PID
Given the gains can be dynamically updated by the simulator (effectively a gain scheduled approach), the integral summer should also multiply by the integral gain `k_i`. Ex:
`integral_sum += error * dt * k_i`

Otherwise, any change in the integral gain can cause transient weirdness in the control loop if the integral gain is updated.

### The model is non-linear
While originally using a canonical spring-mass-damper, it felt unintuitive to have the spring action come from the centre. Given the context of the presentation is vehicular systems, they don't have conventional spring action, but instead have non-linear spring effects (representing friction). As a result, the dynamic model saturates the amount of force given from the spring action to introduce steady-state error for the sake of learning, but also does not attempt to work like a regular spring.

## Slides Link
https://docs.google.com/presentation/d/1qD_pPkHmGp7AkPDejFUIfb_oU5DL514cuSB9fCuW2_M/edit#slide=id.p