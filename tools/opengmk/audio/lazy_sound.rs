    pub(crate) fn ensure_native_sound(&mut self,id:i32)->gml::Result<()> {
        use crate::asset::sound::FileType;
        let sound=self.assets.sounds.get_asset_mut(id).ok_or(gml::Error::NonexistentAsset(asset::Type::Sound,id))?;
        if !matches!(sound.handle,FileType::Deferred{..}) {return Ok(());}
        let FileType::Deferred{data,extension,volume,use_3d,exclusive}=std::mem::replace(&mut sound.handle,FileType::None) else {unreachable!()};
        let bytes=data.as_ref().map_or(0,|d|d.len());
        sound.handle=match data {
            Some(data) if extension.as_ref()==b".wav" =>self.audio.add_wav(data,id,volume,use_3d,exclusive).map(FileType::Wav).unwrap_or(FileType::None),
            Some(data) if extension.as_ref()==b".mp3" =>self.audio.add_mp3(data,id).map(FileType::Mp3).unwrap_or(FileType::None),
            _=>FileType::None,
        };
        // Same None-on-invalid behavior as the original loader, never a fake handle.
        let valid=matches!(sound.handle,FileType::Mp3(_)|FileType::Wav(_));
        crate::diagnostic!("[audio-lazy-register] id={} encoded_bytes={} valid={} requested_volume={} exclusive={} spatial_metadata={}; original asset data not modified",id,bytes,valid,volume,exclusive,use_3d);
        Ok(())
    }
