//! Encoded media retained as deferred assets. No decoder or output is claimed.
use serde::{Serialize,Deserialize};
use crate::host::{unavailable,Service};
#[derive(Clone,Serialize,Deserialize)] pub struct Mp3Handle { _unconstructible: () }
#[derive(Clone,Serialize,Deserialize)] pub struct WavHandle { _unconstructible: () }
impl WavHandle { pub fn set_volume(&self,_vol:f64) { unavailable(Service::Audio,"set_volume") } }
pub struct AudioManager;
impl AudioManager { pub fn deferred() -> Self { Self } }
