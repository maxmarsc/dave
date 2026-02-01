use core::f32;

const BLOCK_SIZE: usize = 4096;
const CHANNELS: usize = 2;

fn main() {
    //============================================================================
    let _test_f64 = 0.0f64;
    let _test_cpx = num_complex::c32(0.0f32, 0.0f32);
    let mut array = [0.0f32; BLOCK_SIZE];
    let mut cpx_array = [num_complex::c32(0.0f32, 0.0f32); BLOCK_SIZE];
    let mut array_array = [[0.0f32; BLOCK_SIZE]; CHANNELS];

    //============================================================================
    let mut vector = vec![0.0f32; BLOCK_SIZE];
    let mut vector_vector = vec![vec![0.0f32; BLOCK_SIZE]; CHANNELS];
    let mut cpx_vector = vec![num_complex::c32(0.0f32, 0.0f32); BLOCK_SIZE];

    //============================================================================
    let mut _array_vector: [Vec<f32>; CHANNELS] = std::array::from_fn(|_| vec![0.0f32; BLOCK_SIZE]);
    let mut _vector_array = vec![[0.0f32; BLOCK_SIZE]; CHANNELS];

    //============================================================================
    let _slice = &mut array[..];
    let _cpx_slice = &mut cpx_array[..];
    let _immut_slice = &vector[..];
    let array_slice = [&array_array[0][..], &array_array[1][..]];
    #[allow(clippy::useless_vec)]
    let _vector_slice = vec![&array_array[0][..], &array_array[1][..]];
    let _slice_slice = &array_slice[..];
    let _slice_array = &array_array[..];
    let _slice_vector = &vector_vector[..];

    //============================================================================

    // Fill with std::sin
    let step_init = 2.0 * std::f32::consts::PI / BLOCK_SIZE as f32 * 16.0;
    let phase_init = 0.0f32;
    (0..BLOCK_SIZE)
        .scan((phase_init, step_init), |(phase, step), i| {
            let val = phase.sin();
            if i % 8 == 0 {
                *step *= 1.01;
            }
            *phase += *step;
            Some(val)
        })
        .zip(array.iter_mut())
        .zip(array_array[0].iter_mut())
        .zip(vector.iter_mut())
        .zip(vector_vector[1].iter_mut())
        .zip(cpx_array.iter_mut())
        .zip(cpx_vector.iter_mut())
        .for_each(
            |(
                (
                    ((((val, array_elm), array_array_elm), vector_elm), vector_vector_elm),
                    cpx_array_elm,
                ),
                cpx_vector_elm,
            )| {
                *array_elm = val;
                *array_array_elm = val * val;
                *vector_elm = -val;
                *vector_vector_elm = -val * val;
                cpx_array_elm.re = val;
                cpx_array_elm.im = -val * val;
                cpx_vector_elm.re = val * val;
                cpx_vector_elm.im = -val;
            },
        );

    // Apply 0.5 gain
    array[0] = 1.0f32;
    array.iter_mut().for_each(|val| *val *= 0.5f32);
    array_array[0].iter_mut().for_each(|val| *val *= 0.5f32);
    vector.iter_mut().for_each(|val| *val *= 0.5f32);
    vector_vector[1].iter_mut().for_each(|val| *val *= 0.5f32);

    // Test some NaN/inf values
    array[0] = f32::NAN;
    array[BLOCK_SIZE / 2] = f32::INFINITY;
    array[BLOCK_SIZE - 1] = -f32::INFINITY;
    vector[0] = f32::NAN;
    vector[BLOCK_SIZE / 2] = f32::INFINITY;
    vector[BLOCK_SIZE - 1] = -f32::INFINITY;
    array_array[0][0] = f32::NAN;
    array_array[0][BLOCK_SIZE / 2] = f32::INFINITY;
    array_array[0][BLOCK_SIZE - 1] = -f32::INFINITY;
    vector_vector[1][0] = f32::NAN;
    vector_vector[1][BLOCK_SIZE / 2] = f32::INFINITY;
    vector_vector[1][BLOCK_SIZE - 1] = -f32::INFINITY;
}
