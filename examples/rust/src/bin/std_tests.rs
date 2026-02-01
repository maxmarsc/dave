use num_complex::{Complex32, Complex64};

const BLOCK_SIZE: usize = 3;
const CHANNELS: usize = 2;
const CPX_ONE: Complex32 = Complex32::new(1.0f32, 1.0f32);
const CPX_ONE_D: Complex64 = Complex64::new(1.0f64, 1.0f64);
const CPX_MINUS_ONE: Complex32 = Complex32::new(-1.0f32, -1.0f32);
const CPX_MINUS_ONE_D: Complex64 = Complex64::new(-1.0f64, -1.0f64);

fn vector_and_slice() {
    ///// std_tests::vector_and_slice::0
    #![allow(clippy::useless_vec)]
    let mut vector_f = vec![0.0f32; BLOCK_SIZE];
    let mut vector_c = vec![num_complex::c32(0.0f32, 0.0f32); BLOCK_SIZE];
    let mut vector_d = vec![0.0f64; BLOCK_SIZE];
    let mut vector_cd = vec![num_complex::c64(0.0f64, 0.0f64); BLOCK_SIZE];
    let _slice_f = &mut vector_f[..];
    let _slice_c = &mut vector_c[..];
    let _slice_d = &mut vector_d[..];
    let _slice_cd = &mut vector_cd[..];
    ///// std_tests::vector_and_slice::1
    vector_f[0] = 1.0;
    vector_d[0] = 1.0;
    vector_c[0] = CPX_ONE;
    vector_cd[0] = CPX_ONE_D;
    vector_f[1] = -1.0;
    vector_d[1] = -1.0;
    vector_c[1] = CPX_MINUS_ONE;
    vector_cd[1] = CPX_MINUS_ONE_D;
    ///// std_tests::vector_and_slice::2
    // Last line to make sure we don't exit
    vector_f[0] = 0.0;
}

fn vector_and_slice_2d() {
    ///// std_tests::vector_and_slice_2d::0
    #![allow(clippy::useless_vec)]
    let mut vector_array_f = vec![[0.0f32; BLOCK_SIZE]; CHANNELS];
    let _vector_slice_f = vec![&vector_array_f[0][..], &vector_array_f[1][..]];
    let _slice_slice_f = &_vector_slice_f[..];
    let _slice_array_f = &vector_array_f[..];
    let mut vector_vector_d = vec![vec![0.0f64; BLOCK_SIZE]; CHANNELS];
    let _slice_vector_d = &vector_vector_d[..];
    ///// std_tests::vector_and_slice_2d::1
    vector_array_f[1][0] = 1.0;
    vector_vector_d[1][0] = 1.0;
    vector_array_f[1][1] = -1.0;
    vector_vector_d[1][1] = -1.0;
    ///// std_tests::vector_and_slice_2d::2
    vector_array_f[0][0] = 0.0;
}

fn array() {
    ///// std_tests::array::0
    let mut array_f = [0.0f32; BLOCK_SIZE];
    let mut array_c = [num_complex::c32(0.0f32, 0.0f32); BLOCK_SIZE];
    let mut array_d = [0.0f64; BLOCK_SIZE];
    let mut array_cd = [num_complex::c64(0.0f64, 0.0f64); BLOCK_SIZE];
    ///// std_tests::array::1
    array_f[0] = 1.0;
    array_d[0] = 1.0;
    array_c[0] = CPX_ONE;
    array_cd[0] = CPX_ONE_D;
    array_f[1] = -1.0;
    array_d[1] = -1.0;
    array_c[1] = CPX_MINUS_ONE;
    array_cd[1] = CPX_MINUS_ONE_D;
    ///// std_tests::array::2
    array_f[0] = 0.0;
}

fn array_2d() {
    ///// std_tests::array_2d::0
    let mut array_array_f = [[0.0f32; BLOCK_SIZE]; CHANNELS];
    let _array_slice_f = [&array_array_f[0][..], &array_array_f[1][..]];
    let mut array_vector_d = [vec![0.0f64; BLOCK_SIZE], vec![0.0f64; BLOCK_SIZE]];
    ///// std_tests::array_2d::1
    array_array_f[1][0] = 1.0;
    array_vector_d[1][0] = 1.0;
    array_array_f[1][1] = -1.0;
    array_vector_d[1][1] = -1.0;
    ///// std_tests::array_2d::2
    array_array_f[0][0] = 0.0;
}

fn main() {
    vector_and_slice();
    vector_and_slice_2d();
    array();
    array_2d();
}
