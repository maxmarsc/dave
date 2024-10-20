import numpy as np
import cmath

# import dave.server.debuggers.pdb as pydave


BLOCK_SIZE = 4096
CHANNELS = 2


def compute_phase() -> np.ndarray:
    phase_array = np.zeros((BLOCK_SIZE,))
    step = 2 * np.pi / BLOCK_SIZE * 16
    phase = 0.0

    for i in range(BLOCK_SIZE):
        phase_array[i] = phase
        phase += step
        if i % 8 == 0:
            step *= 1.01

    return phase_array


def main():
    array_1D = np.zeros((BLOCK_SIZE,))
    array_2D = np.zeros((CHANNELS, BLOCK_SIZE))

    cpx_array_1D = np.zeros((BLOCK_SIZE,), dtype=np.complex64)
    cpx_array_2D = np.zeros((CHANNELS, BLOCK_SIZE), dtype=np.complex64)
    cpx_array_1D_2 = np.zeros((BLOCK_SIZE, 2), dtype=np.float32)
    cpx_array_2D_2 = np.zeros((CHANNELS, BLOCK_SIZE, 2), dtype=np.float32)
    phase = compute_phase()

    # Fill with sin
    array_1D[:] = np.sin(phase)
    array_2D[0][:] = np.sin(phase)
    array_2D[1][:] = -np.sin(phase)
    cpx_array_1D[:] = np.sin(phase) - np.sin(phase) * 1j
    cpx_array_2D[1][:] = -np.sin(phase) - np.sin(phase) * 1j
    cpx_array_1D_2.view(np.complex64)[:, 0] = np.sin(phase) - np.sin(phase) * 1j
    cpx_array_2D_2.view(np.complex64)[0][:, 0] = -np.sin(phase) + np.sin(phase) * 1j

    # Apply 0.5 gain
    array_1D *= 0.5
    array_2D *= 0.5

    print("Done")


if __name__ == "__main__":
    main()
