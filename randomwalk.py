import numpy as np
import matplotlib.pyplot as plt

def simple_random(steps=1000):
        """Generates a simple random walk."""
        return np.random.choice([-1, 1], size=steps).cumsum()
    
def plot_random_walk(steps=1000):
    """Plots a simple random walk."""
    walk = simple_random(steps)
    plt.figure(figsize=(10, 6))
    plt.plot(walk, label='Random Walk')
    plt.title('Simple Random Walk')
    plt.xlabel('Steps')
    plt.ylabel('Position')
    plt.axhline(0, color='black', lw=0.5, ls='--')
    plt.grid()
    plt.legend()
    plt.show()
    
def random_walk_with_drift(steps=1000, drift=0.01):
    """Generates a random walk with a drift."""
    steps = np.random.choice([-1, 1], size=steps)
    drift_steps = np.full(steps.shape, drift)
    return (steps + drift_steps).cumsum()

def plot_random_walk_with_drift(steps=1000, drift=0.01):
    """Plots a random walk with a drift."""
    walk = random_walk_with_drift(steps, drift)
    plt.figure(figsize=(10, 6))
    plt.plot(walk, label='Random Walk with Drift')
    plt.title('Random Walk with Drift')
    plt.xlabel('Steps')
    plt.ylabel('Position')
    plt.axhline(0, color='black', lw=0.5, ls='--')
    plt.grid()
    plt.legend()
    plt.show()
    
def random_walk_with_drift_and_volatility(steps=1000, drift=0.01, volatility=0.1):
    """Generates a random walk with drift and volatility."""
    steps = np.random.normal(loc=drift, scale=volatility, size=steps)
    return steps.cumsum()


def plot_random_walk_with_drift_and_volatility(steps=1000, drift=0.01, volatility=0.1):
    """Plots a random walk with drift and volatility."""
    walk = random_walk_with_drift_and_volatility(steps, drift, volatility)
    plt.figure(figsize=(10, 6))
    plt.plot(walk, label='Random Walk with Drift and Volatility')
    plt.title('Random Walk with Drift and Volatility')
    plt.xlabel('Steps')
    plt.ylabel('Position')
    plt.axhline(0, color='black', lw=0.5, ls='--')
    plt.grid()
    plt.legend()
    plt.show()
    
    
def random_walk_with_drift_volatility_and_trend(steps=1000, drift=0.01, volatility=0.1, trend=0.001):
    """Generates a random walk with drift, volatility, and trend."""
    steps = np.random.normal(loc=drift + trend, scale=volatility, size=steps)
    return steps.cumsum()

def plot_random_walk_with_drift_volatility_and_trend(steps=1000, drift=0.01, volatility=0.1, trend=0.001):
    """Plots a random walk with drift, volatility, and trend."""
    walk = random_walk_with_drift_volatility_and_trend(steps, drift, volatility, trend)
    plt.figure(figsize=(10, 6))
    plt.plot(walk, label='Random Walk with Drift, Volatility, and Trend')
    plt.title('Random Walk with Drift, Volatility, and Trend')
    plt.xlabel('Steps')
    plt.ylabel('Position')
    plt.axhline(0, color='black', lw=0.5, ls='--')
    plt.grid()
    plt.legend()
    plt.show()
    