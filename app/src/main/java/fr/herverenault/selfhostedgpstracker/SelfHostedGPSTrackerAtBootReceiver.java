package fr.herverenault.selfhostedgpstracker;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;

/**
 * Broadcast receiver to enable the self hosted GPS tracker at boot.
 * Created by Kees Jongenburger on 08/12/15.
 */
public class SelfHostedGPSTrackerAtBootReceiver extends BroadcastReceiver {

    private static final String TAG = SelfHostedGPSTrackerAtBootReceiver.class.getSimpleName();

    /**
     *  Upon receiving the boot complete intent start the Self hosted GPS tracker
     *  service if configured do to so
     * */
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context.getApplicationContext());
            /* If the device is configured to start on boot start the application */
            if (preferences.getBoolean("pref_start_on_boot",false)){
                Log.i(TAG,"Starting Self hosted GPS tracker");
                Intent serviceIntent = new Intent(context, SelfHostedGPSTrackerService.class);
                context.startService(serviceIntent);
            } else {
                Log.d(TAG,"Not starting the Self hosted GPS tracker");
            }
        }
    }
}
