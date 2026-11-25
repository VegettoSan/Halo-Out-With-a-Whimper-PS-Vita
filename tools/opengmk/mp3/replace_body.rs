        #[cfg(feature="headless")] {
            let (sound_id,fname,kind,preload)=expect_args!(args,[int,string,int,bool])?;
            crate::host::trace("sound_replace");
            let sound=self.assets.sounds.get_asset(sound_id).ok_or_else(||gml::Error::FunctionError("sound_replace".into(),"Trying to replace non-existing sound.".into()))?;
            let old=match sound.handle {asset::sound::FileType::Deferred{..}=>"Deferred",asset::sound::FileType::None=>"None",asset::sound::FileType::Mp3(_)=>"Mp3",_=>"other"};
            crate::diagnostic!("[sound-replace-request] id={} old={} kind={} preload={}; no output stream active",sound_id,old,kind,preload);
            let path=std::path::PathBuf::from(fname.as_ref().replace('\\',"/"));
            if !path.extension().is_some_and(|x|x.eq_ignore_ascii_case("mp3")) {
                crate::diagnostic!("[sound-replace-failed] id={} reason=unsupported_format old_preserved=true",sound_id);return Ok(0.into());
            }
            // Decode before modifying the registry. Failed replacement cannot install a fake handle.
            let data=match std::fs::read(&path) {
                Ok(b)=>b.into_boxed_slice(),Err(e)=>{crate::diagnostic!("[sound-replace-failed] id={} io={} old_preserved=true",sound_id,e);return Ok(0.into());}
            };
            let handle=match self.audio.add_mp3(data,sound_id) {Some(h)=>h,None=>{
                crate::diagnostic!("[sound-replace-failed] id={} reason=decode old_preserved=true",sound_id);return Ok(0.into());
            }};
            let details=crate::game::audio::AudioManager::registered_details(&handle);
            let sound=self.assets.sounds.get_asset_mut(sound_id).unwrap();
            sound.handle=asset::sound::FileType::Mp3(handle);
            sound.gml_kind=kind.into();sound.gml_preload=f64::from(u8::from(preload)).into();
            crate::diagnostic!("[sound-replace-registered] id={} encoded_bytes={} channels={} rate={} samples_per_channel={} kind={} preload={} result=1 output_started=false",details.0,details.1,details.2,details.3,details.4,kind,preload);
            Ok(1.into())
        }
