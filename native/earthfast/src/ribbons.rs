//! roadmesh.ribbons' resampling and mitred normals for many chunks at once (roadmesh._resample + _normals: numpy
//! calls per chunk were ~0.9 s of 8 Bratislava road tiles, 2026-10-28). The same float64 operations as numpy's, in
//! its order: the results equal the numpy version's bit for bit.

use numpy::{IntoPyArray, PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;

/// numpy.interp for increasing xp (x at or past the last xp: fp's last value).
fn interp(x: f64, xp: &[f64], fp: &[f64]) -> f64 {
    let n = xp.len();
    if x <= xp[0] {
        return fp[0];
    }
    if x >= xp[n - 1] {
        return fp[n - 1];
    }
    // the last j with xp[j] <= x
    let mut lo = 0usize;
    let mut hi = n - 1;
    while hi - lo > 1 {
        let mid = (lo + hi) / 2;
        if xp[mid] <= x { lo = mid } else { hi = mid }
    }
    let slope = (fp[lo + 1] - fp[lo]) / (xp[lo + 1] - xp[lo]);
    let v = slope * (x - xp[lo]) + fp[lo];
    if v.is_nan() {
        // (numpy: a zero-length step's slope is nan: then the side value)
        let w = slope * (x - xp[lo + 1]) + fp[lo + 1];
        if w.is_nan() && fp[lo] == fp[lo + 1] { return fp[lo]; }
        return w;
    }
    v
}

/// Per chunk c (points pts[off[c]..off[c + 1]] (k, 3)): resampled every `step` m with its ends kept (numpy's
/// linspace), and the left / right edges at half[c] m along the mitred normals (cos clipped at 0.5). Returns (left
/// (m, 2), right (m, 2), arc s (m,), z (m,), out offsets (chunks + 1)); a chunk of zero length gives its first point.
#[pyfunction]
#[allow(clippy::type_complexity)]
pub fn ribbon_edges<'py>(py: Python<'py>, pts: PyReadonlyArray2<'py, f64>, off: PyReadonlyArray1<'py, i64>,
                         half: PyReadonlyArray1<'py, f64>, step: f64)
                         -> (Bound<'py, PyArray2<f64>>, Bound<'py, PyArray2<f64>>, Bound<'py, PyArray1<f64>>,
                             Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<i64>>) {
    let (pts, off, half) = (pts.as_array(), off.as_array(), half.as_array());
    let (l, r, s_out, z_out, o) = py.allow_threads(|| {
        let mut l: Vec<f64> = Vec::new();
        let mut r: Vec<f64> = Vec::new();
        let mut s_out: Vec<f64> = Vec::new();
        let mut z_out: Vec<f64> = Vec::new();
        let mut o: Vec<i64> = vec![0];
        for c in 0..off.len().saturating_sub(1) {
            let (a, b) = (off[c] as usize, off[c + 1] as usize);
            let k = b - a;
            let (px, py_, pz): (Vec<f64>, Vec<f64>, Vec<f64>) =
                ((a..b).map(|i| pts[[i, 0]]).collect(), (a..b).map(|i| pts[[i, 1]]).collect(),
                 (a..b).map(|i| pts[[i, 2]]).collect());
            let mut s = vec![0.0f64; k];
            for i in 1..k {
                s[i] = s[i - 1] + (px[i] - px[i - 1]).hypot(py_[i] - py_[i - 1]);
            }
            let (xs, ys, ts, zs): (Vec<f64>, Vec<f64>, Vec<f64>, Vec<f64>);
            if k == 0 {
                o.push(l.len() as i64 / 2);
                continue;
            }
            if s[k - 1] <= 1e-6 {
                xs = vec![px[0]]; ys = vec![py_[0]]; ts = vec![s[0]]; zs = vec![pz[0]];
            } else {
                let n = 1usize.max((s[k - 1] / step).ceil() as usize);
                // numpy.linspace(0, stop, n + 1): step = stop / n, t[i] = i * step, the last exactly stop
                let st = s[k - 1] / n as f64;
                let t: Vec<f64> = (0..=n).map(|i| if i == n { s[k - 1] } else { i as f64 * st }).collect();
                xs = t.iter().map(|&x| interp(x, &s, &px)).collect();
                ys = t.iter().map(|&x| interp(x, &s, &py_)).collect();
                zs = t.iter().map(|&x| interp(x, &s, &pz)).collect();
                ts = t;
            }
            let m = xs.len();
            // _normals (times half)
            let mut nx = vec![0.0f64; m];
            let mut ny = vec![0.0f64; m];
            if m >= 2 {
                let mut snx = vec![0.0f64; m - 1];
                let mut sny = vec![0.0f64; m - 1];
                for i in 0..m - 1 {
                    let (dx, dy) = (xs[i + 1] - xs[i], ys[i + 1] - ys[i]);
                    let mut len = dx.hypot(dy);
                    if len < 1e-9 { len = 1e-9; }
                    let (tx, ty) = (dx / len, dy / len);
                    snx[i] = -ty;
                    sny[i] = tx;
                }
                nx[0] = snx[0]; ny[0] = sny[0];
                nx[m - 1] = snx[m - 2]; ny[m - 1] = sny[m - 2];
                for i in 1..m - 1 {
                    let (mx, my) = (snx[i - 1] + snx[i], sny[i - 1] + sny[i]);
                    let mut ml = mx.hypot(my);
                    if ml < 1e-9 { ml = 1.0; }
                    let (mx, my) = (mx / ml, my / ml);
                    let cos = (mx * snx[i] + my * sny[i]).clamp(0.5, 1.0);
                    nx[i] = mx / cos;
                    ny[i] = my / cos;
                }
            }
            for i in 0..m {
                let (hx, hy) = (nx[i] * half[c], ny[i] * half[c]);
                l.push(xs[i] + hx); l.push(ys[i] + hy);
                r.push(xs[i] - hx); r.push(ys[i] - hy);
                s_out.push(ts[i]);
                z_out.push(zs[i]);
            }
            o.push(s_out.len() as i64);
        }
        (l, r, s_out, z_out, o)
    });
    let m = s_out.len();
    (numpy::ndarray::Array2::from_shape_vec((m, 2), l).expect("left").into_pyarray(py),
     numpy::ndarray::Array2::from_shape_vec((m, 2), r).expect("right").into_pyarray(py),
     s_out.into_pyarray(py), z_out.into_pyarray(py), o.into_pyarray(py))
}
